import logging
from celery import shared_task
from django.utils import timezone
from django.db import models
from datetime import timedelta, datetime
from .services import social_media_service
from .models import (
    SocialMediaPost,
    SocialMediaSchedule,
    SocialMediaAccount,
    SocialMediaCampaign,
    SocialMediaHashtag,
    SocialMediaAnalytics,
)
from core.models import User

logger = logging.getLogger("social_media.tasks")


@shared_task(bind=True, max_retries=3)
def post_to_social_media(self, post_id):
    """Post content to social media platform"""
    try:
        post = SocialMediaPost.objects.get(id=post_id)

        result = social_media_service.post_content(
            platform=post.platform,
            content=post.content,
            user=post.user,
            media_urls=post.media_urls,
        )

        # Update post with results
        post.platform_post_id = result.get("post_id")
        post.platform_url = result.get("url")
        post.status = "PUBLISHED"
        post.published_at = timezone.now()
        post.save()

        logger.info(f"Successfully posted to {post.platform}: {post_id}")
        return result

    except Exception as e:
        logger.error(f"Failed to post to social media: {e}")

        # Update post status
        try:
            post = SocialMediaPost.objects.get(id=post_id)
            post.status = "FAILED"
            post.error_message = str(e)
            post.save()
        except:
            pass

        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))


@shared_task
def process_scheduled_posts():
    """Process social media posts that are scheduled for now"""
    try:
        # Get posts scheduled for now or earlier
        due_schedules = SocialMediaSchedule.objects.filter(
            scheduled_time__lte=timezone.now(), is_processed=False
        ).select_related("post")

        processed_count = 0

        for schedule in due_schedules:
            try:
                # Post the content
                post_to_social_media.delay(str(schedule.post.id))

                # Mark schedule as processed
                schedule.is_processed = True
                schedule.processed_at = timezone.now()
                schedule.save()

                processed_count += 1

            except Exception as e:
                logger.error(f"Failed to process scheduled post {schedule.id}: {e}")

                # Handle retry logic
                if schedule.retry_count < schedule.max_retries:
                    schedule.retry_count += 1
                    schedule.next_retry = timezone.now() + timedelta(
                        minutes=5 * schedule.retry_count
                    )
                    schedule.save()
                else:
                    # Mark as failed after max retries
                    schedule.is_processed = True
                    schedule.processed_at = timezone.now()
                    schedule.error_message = str(e)
                    schedule.save()

                    # Update post status
                    schedule.post.status = "FAILED"
                    schedule.post.error_message = f"Max retries exceeded: {str(e)}"
                    schedule.post.save()

        logger.info(f"Processed {processed_count} scheduled posts")
        return processed_count

    except Exception as e:
        logger.error(f"Failed to process scheduled posts: {e}")
        raise


@shared_task
def update_social_media_metrics():
    """Update metrics for recent social media posts"""
    try:
        # Get posts from the last 7 days that need metric updates
        cutoff_date = timezone.now() - timedelta(days=7)

        posts_to_update = SocialMediaPost.objects.filter(
            status="PUBLISHED",
            published_at__gte=cutoff_date,
            platform_post_id__isnull=False,
        ).filter(
            # Only update if metrics haven't been updated in the last hour
            models.Q(last_metrics_update__isnull=True)
            | models.Q(last_metrics_update__lt=timezone.now() - timedelta(hours=1))
        )

        updated_count = 0

        for post in posts_to_update:
            try:
                # Get updated metrics from platform
                analytics = social_media_service.get_post_analytics(
                    post_id=post.platform_post_id, platform=post.platform
                )

                if analytics:
                    post.metrics = analytics
                    post.last_metrics_update = timezone.now()
                    post.save()
                    updated_count += 1

            except Exception as e:
                logger.error(f"Failed to update metrics for post {post.id}: {e}")

        logger.info(f"Updated metrics for {updated_count} posts")
        return updated_count

    except Exception as e:
        logger.error(f"Failed to update social media metrics: {e}")
        raise


@shared_task
def generate_campaign_content(campaign_id):
    """Generate content for a social media campaign"""
    try:
        campaign = SocialMediaCampaign.objects.get(id=campaign_id)

        if not campaign.use_ai_content:
            logger.info(f"AI content disabled for campaign {campaign_id}")
            return

        # Import AI agent tasks to avoid circular imports
        from ai_agents.tasks import generate_ai_content

        generated_posts = []

        for platform in campaign.platforms:
            template = campaign.content_templates.get(platform, {})

            if template:
                # Generate AI content based on template
                prompt = f"""Create a {platform} post for the campaign: {campaign.name}
                
                Campaign Description: {campaign.description}
                Tone: {campaign.ai_tone}
                Guidelines: {campaign.ai_guidelines}
                
                Template: {template}
                """

                # Queue AI content generation
                result = generate_ai_content.delay(
                    user_id=str(campaign.user.id),
                    agent_type="MARKETING",
                    prompt=prompt,
                    context={
                        "campaign_id": str(campaign.id),
                        "platform": platform,
                        "campaign_type": "social_media",
                    },
                )

                generated_posts.append({"platform": platform, "task_id": result.id})

        logger.info(f"Queued content generation for campaign {campaign_id}")
        return generated_posts

    except Exception as e:
        logger.error(f"Failed to generate campaign content: {e}")
        raise


@shared_task
def bulk_schedule_posts(posts_data, user_id):
    """Schedule multiple posts in bulk"""
    try:
        user = User.objects.get(id=user_id)
        scheduled_posts = []

        for post_data in posts_data:
            try:
                # Create the post
                post = SocialMediaPost.objects.create(
                    user=user,
                    platform=post_data["platform"],
                    content=post_data["content"],
                    media_urls=post_data.get("media_urls", []),
                    status="SCHEDULED",
                    scheduled_time=datetime.fromisoformat(post_data["scheduled_time"]),
                    is_ai_generated=post_data.get("is_ai_generated", False),
                    campaign_id=post_data.get("campaign_id", ""),
                )

                # Create the schedule
                schedule = SocialMediaSchedule.objects.create(
                    post=post, scheduled_time=post.scheduled_time
                )

                scheduled_posts.append(
                    {
                        "post_id": str(post.id),
                        "schedule_id": str(schedule.id),
                        "platform": post.platform,
                        "scheduled_time": post.scheduled_time.isoformat(),
                    }
                )

            except Exception as e:
                logger.error(f"Failed to schedule post: {e}")
                scheduled_posts.append({"error": str(e), "post_data": post_data})

        logger.info(f"Bulk scheduled {len(scheduled_posts)} posts for user {user_id}")
        return scheduled_posts

    except Exception as e:
        logger.error(f"Failed to bulk schedule posts: {e}")
        raise


@shared_task
def sync_social_accounts():
    """Sync social media account information"""
    try:
        accounts = SocialMediaAccount.objects.filter(status="ACTIVE")
        updated_count = 0

        for account in accounts:
            try:
                # Check if token is still valid
                if not account.is_token_valid:
                    account.status = "ERROR"
                    account.save()
                    continue

                # Update account information (this would vary by platform)
                # For now, just update last sync time
                account.last_sync = timezone.now()
                account.save()
                updated_count += 1

            except Exception as e:
                logger.error(f"Failed to sync account {account.id}: {e}")
                account.status = "ERROR"
                account.save()

        logger.info(f"Synced {updated_count} social media accounts")
        return updated_count

    except Exception as e:
        logger.error(f"Failed to sync social accounts: {e}")
        raise


@shared_task
def update_trending_hashtags():
    """Update trending hashtags from various platforms"""
    try:
        # This would integrate with platform APIs to get trending hashtags
        # For now, we'll simulate the process

        trending_tags = [
            "#crypto",
            "#blockchain",
            "#defi",
            "#nft",
            "#web3",
            "#bitcoin",
            "#ethereum",
            "#altcoin",
            "#tokenlaunch",
        ]

        updated_count = 0

        for tag in trending_tags:
            hashtag, created = SocialMediaHashtag.objects.get_or_create(
                tag=tag.replace("#", ""),
                defaults={
                    "category": "crypto",
                    "trending_score": 100,
                    "is_trending": True,
                },
            )

            if not created:
                # Update existing hashtag
                hashtag.trending_score += 10
                hashtag.is_trending = True
                hashtag.last_updated = timezone.now()
                hashtag.save()

            updated_count += 1

        # Decay trending scores for older hashtags
        old_hashtags = SocialMediaHashtag.objects.filter(
            last_updated__lt=timezone.now() - timedelta(hours=6)
        )

        for hashtag in old_hashtags:
            hashtag.trending_score = max(0, hashtag.trending_score - 5)
            hashtag.is_trending = hashtag.trending_score > 50
            hashtag.save()

        logger.info(f"Updated {updated_count} trending hashtags")
        return updated_count

    except Exception as e:
        logger.error(f"Failed to update trending hashtags: {e}")
        raise


@shared_task
def generate_daily_social_analytics():
    """Generate daily analytics for social media performance"""
    try:
        yesterday = timezone.now().date() - timedelta(days=1)

        # Get all users with social media activity
        active_users = User.objects.filter(
            social_posts__published_at__date=yesterday
        ).distinct()

        analytics_created = 0

        for user in active_users:
            for platform in ["TWITTER", "LINKEDIN", "FACEBOOK", "INSTAGRAM"]:
                # Get posts for this user/platform/date
                posts = SocialMediaPost.objects.filter(
                    user=user,
                    platform=platform,
                    published_at__date=yesterday,
                    status="PUBLISHED",
                )

                if not posts.exists():
                    continue

                # Calculate metrics
                total_reach = sum(post.metrics.get("reach", 0) for post in posts)
                total_impressions = sum(
                    post.metrics.get("impressions", 0) for post in posts
                )
                total_engagement = sum(
                    post.metrics.get("likes", 0)
                    + post.metrics.get("comments", 0)
                    + post.metrics.get("shares", 0)
                    for post in posts
                )

                # Calculate engagement rate
                avg_engagement_rate = (
                    sum(post.engagement_rate for post in posts) / posts.count()
                    if posts.count() > 0
                    else 0
                )

                # Create or update analytics record
                analytics, created = SocialMediaAnalytics.objects.get_or_create(
                    user=user,
                    date=yesterday,
                    platform=platform,
                    defaults={
                        "posts_published": posts.count(),
                        "total_reach": total_reach,
                        "total_impressions": total_impressions,
                        "total_engagement": total_engagement,
                        "average_engagement_rate": avg_engagement_rate,
                    },
                )

                if created:
                    analytics_created += 1

        logger.info(f"Generated {analytics_created} daily social analytics records")
        return analytics_created

    except Exception as e:
        logger.error(f"Failed to generate daily social analytics: {e}")
        raise


@shared_task
def cleanup_failed_posts():
    """Clean up old failed posts and schedules"""
    try:
        # Clean up failed posts older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)

        failed_posts = SocialMediaPost.objects.filter(
            status="FAILED", created_at__lt=cutoff_date
        )

        failed_count = failed_posts.count()
        failed_posts.delete()

        # Clean up processed schedules older than 7 days
        old_schedules = SocialMediaSchedule.objects.filter(
            is_processed=True, processed_at__lt=timezone.now() - timedelta(days=7)
        )

        schedule_count = old_schedules.count()
        old_schedules.delete()

        logger.info(
            f"Cleaned up {failed_count} failed posts and {schedule_count} old schedules"
        )
        return {
            "failed_posts_cleaned": failed_count,
            "schedules_cleaned": schedule_count,
        }

    except Exception as e:
        logger.error(f"Failed to cleanup failed posts: {e}")
        raise


@shared_task
def process_social_webhooks(webhook_data):
    """Process incoming webhooks from social media platforms"""
    try:
        from .models import SocialMediaWebhook

        # Create webhook record
        webhook = SocialMediaWebhook.objects.create(
            platform=webhook_data["platform"],
            event_type=webhook_data["event_type"],
            event_id=webhook_data["event_id"],
            event_data=webhook_data["data"],
            raw_payload=webhook_data["raw_payload"],
        )

        # Process based on event type
        if webhook_data["event_type"] == "POST_PUBLISHED":
            # Update post status if we have a matching post
            try:
                post = SocialMediaPost.objects.get(
                    platform_post_id=webhook_data["data"]["post_id"]
                )
                post.status = "PUBLISHED"
                post.published_at = timezone.now()
                post.save()
            except SocialMediaPost.DoesNotExist:
                pass

        elif webhook_data["event_type"] in ["LIKE", "COMMENT", "SHARE"]:
            # Update post metrics
            try:
                post = SocialMediaPost.objects.get(
                    platform_post_id=webhook_data["data"]["post_id"]
                )
                # Queue metrics update
                update_social_media_metrics.delay()
            except SocialMediaPost.DoesNotExist:
                pass

        # Mark webhook as processed
        webhook.is_processed = True
        webhook.processed_at = timezone.now()
        webhook.save()

        logger.info(f"Processed webhook: {webhook.id}")
        return str(webhook.id)

    except Exception as e:
        logger.error(f"Failed to process social webhook: {e}")
        raise


@shared_task
def optimize_posting_schedule(user_id, platform):
    """Analyze and optimize posting schedule for user"""
    try:
        user = User.objects.get(id=user_id)

        # Analyze past performance to find optimal posting times
        posts = SocialMediaPost.objects.filter(
            user=user,
            platform=platform,
            status="PUBLISHED",
            published_at__gte=timezone.now() - timedelta(days=30),
        ).exclude(metrics={})

        if not posts.exists():
            logger.info(
                f"No data available for optimization: user {user_id}, platform {platform}"
            )
            return None

        # Analyze performance by hour of day
        hour_performance = {}

        for post in posts:
            hour = post.published_at.hour
            engagement_rate = post.engagement_rate

            if hour not in hour_performance:
                hour_performance[hour] = {"total_engagement": 0, "post_count": 0}

            hour_performance[hour]["total_engagement"] += engagement_rate
            hour_performance[hour]["post_count"] += 1

        # Calculate average engagement by hour
        optimal_hours = []
        for hour, data in hour_performance.items():
            avg_engagement = data["total_engagement"] / data["post_count"]
            optimal_hours.append((hour, avg_engagement))

        # Sort by engagement rate
        optimal_hours.sort(key=lambda x: x[1], reverse=True)

        # Get top 3 hours
        best_hours = [hour for hour, _ in optimal_hours[:3]]

        logger.info(
            f"Optimal posting hours for user {user_id} on {platform}: {best_hours}"
        )
        return {
            "user_id": user_id,
            "platform": platform,
            "optimal_hours": best_hours,
            "analysis_period": "30 days",
            "posts_analyzed": posts.count(),
        }

    except Exception as e:
        logger.error(f"Failed to optimize posting schedule: {e}")
        raise
