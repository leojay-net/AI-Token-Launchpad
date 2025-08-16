import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
import tweepy
import requests
from .models import SocialMediaPost, SocialMediaAccount, SocialMediaSchedule
from core.models import User

logger = logging.getLogger("social_media")


class SocialMediaError(Exception):
    """Custom exception for social media service errors"""

    pass


class RateLimitExceeded(SocialMediaError):
    """Exception raised when social media rate limit is exceeded"""

    pass


class SocialMediaService:
    """Main service for social media operations"""

    def __init__(self):
        self.platforms = {
            "twitter": TwitterService(),
            "linkedin": LinkedInService(),
            "facebook": FacebookService(),
            "instagram": InstagramService(),
        }

    async def post_content(
        self,
        platform: str,
        content: str,
        user: User,
        media_urls: Optional[List[str]] = None,
        scheduled_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Post content to social media platform"""

        if platform not in self.platforms:
            raise SocialMediaError(f"Platform {platform} not supported")

        try:
            service = self.platforms[platform]

            if scheduled_time and scheduled_time > timezone.now():
                # Schedule the post
                return await self._schedule_post(
                    platform, content, user, media_urls, scheduled_time
                )
            else:
                # Post immediately
                result = await service.post(content, user, media_urls)

                # Record the post
                post = await self._record_post(
                    platform=platform,
                    content=content,
                    user=user,
                    media_urls=media_urls or [],
                    post_id=result.get("post_id"),
                    status="published",
                    metrics=result.get("metrics", {}),
                )

                return {
                    "success": True,
                    "post_id": result.get("post_id"),
                    "platform": platform,
                    "url": result.get("url"),
                    "record_id": post.id,
                }

        except Exception as e:
            logger.error(f"Failed to post to {platform}: {e}")

            # Record failed post
            await self._record_post(
                platform=platform,
                content=content,
                user=user,
                media_urls=media_urls or [],
                status="failed",
                error_message=str(e),
            )

            raise SocialMediaError(f"Failed to post to {platform}: {e}")

    async def _schedule_post(
        self,
        platform: str,
        content: str,
        user: User,
        media_urls: Optional[List[str]],
        scheduled_time: datetime,
    ) -> Dict[str, Any]:
        """Schedule a post for later"""

        # Create scheduled post record
        post = await self._record_post(
            platform=platform,
            content=content,
            user=user,
            media_urls=media_urls or [],
            status="scheduled",
            scheduled_time=scheduled_time,
        )

        # Create schedule entry
        schedule = SocialMediaSchedule.objects.create(
            post=post, scheduled_time=scheduled_time, is_processed=False
        )

        return {
            "success": True,
            "scheduled": True,
            "schedule_id": schedule.id,
            "scheduled_time": scheduled_time.isoformat(),
            "record_id": post.id,
        }

    async def _record_post(
        self,
        platform: str,
        content: str,
        user: User,
        media_urls: List[str],
        post_id: Optional[str] = None,
        status: str = "draft",
        scheduled_time: Optional[datetime] = None,
        metrics: Optional[Dict] = None,
        error_message: Optional[str] = None,
    ) -> SocialMediaPost:
        """Record social media post in database"""

        post = SocialMediaPost.objects.create(
            user=user,
            platform=platform,
            content=content,
            media_urls=media_urls,
            post_id=post_id,
            status=status,
            scheduled_time=scheduled_time,
            metrics=metrics or {},
            error_message=error_message,
        )

        return post

    async def get_post_analytics(self, post_id: str, platform: str) -> Dict[str, Any]:
        """Get analytics for a specific post"""

        if platform not in self.platforms:
            raise SocialMediaError(f"Platform {platform} not supported")

        service = self.platforms[platform]
        return await service.get_analytics(post_id)

    async def bulk_post(
        self, posts: List[Dict], user: User, delay_seconds: int = 30
    ) -> List[Dict[str, Any]]:
        """Post multiple pieces of content with delays"""

        results = []

        for i, post_data in enumerate(posts):
            try:
                if i > 0:  # Add delay between posts
                    await asyncio.sleep(delay_seconds)

                result = await self.post_content(
                    platform=post_data["platform"],
                    content=post_data["content"],
                    user=user,
                    media_urls=post_data.get("media_urls"),
                    scheduled_time=post_data.get("scheduled_time"),
                )
                results.append(result)

            except Exception as e:
                logger.error(f"Failed bulk post {i}: {e}")
                results.append(
                    {"success": False, "error": str(e), "post_data": post_data}
                )

        return results

    async def process_scheduled_posts(self):
        """Process scheduled posts that are due"""

        due_schedules = SocialMediaSchedule.objects.filter(
            scheduled_time__lte=timezone.now(), is_processed=False
        ).select_related("post")

        for schedule in due_schedules:
            try:
                post = schedule.post
                service = self.platforms[post.platform]

                result = await service.post(post.content, post.user, post.media_urls)

                # Update post record
                post.post_id = result.get("post_id")
                post.status = "published"
                post.metrics = result.get("metrics", {})
                post.published_at = timezone.now()
                post.save()

                # Mark schedule as processed
                schedule.is_processed = True
                schedule.processed_at = timezone.now()
                schedule.save()

                logger.info(f"Successfully posted scheduled content: {post.id}")

            except Exception as e:
                logger.error(f"Failed to post scheduled content {schedule.id}: {e}")

                # Update post with error
                schedule.post.status = "failed"
                schedule.post.error_message = str(e)
                schedule.post.save()

                # Mark schedule as processed (with error)
                schedule.is_processed = True
                schedule.processed_at = timezone.now()
                schedule.error_message = str(e)
                schedule.save()


class TwitterService:
    """Twitter/X API service"""

    def __init__(self):
        self.setup_client()

    def setup_client(self):
        """Initialize Twitter API client"""
        try:
            if all(
                [
                    settings.TWITTER_API_KEY,
                    settings.TWITTER_API_SECRET,
                    settings.TWITTER_ACCESS_TOKEN,
                    settings.TWITTER_ACCESS_SECRET,
                ]
            ):
                self.client = tweepy.Client(
                    consumer_key=settings.TWITTER_API_KEY,
                    consumer_secret=settings.TWITTER_API_SECRET,
                    access_token=settings.TWITTER_ACCESS_TOKEN,
                    access_token_secret=settings.TWITTER_ACCESS_SECRET,
                    wait_on_rate_limit=True,
                )
                logger.info("Twitter client initialized successfully")
            else:
                self.client = None
                logger.warning("Twitter API credentials not configured")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
            self.client = None

    async def post(
        self, content: str, user: User, media_urls: Optional[List[str]] = None
    ) -> Dict:
        """Post tweet"""
        if not self.client:
            raise SocialMediaError("Twitter client not configured")

        try:
            # Check rate limits
            if not self._check_rate_limit(user):
                raise RateLimitExceeded("Twitter rate limit exceeded")

            # Handle media uploads if provided
            media_ids = []
            if media_urls:
                media_ids = await self._upload_media(media_urls)

            # Post tweet
            if media_ids:
                response = self.client.create_tweet(text=content, media_ids=media_ids)
            else:
                response = self.client.create_tweet(text=content)

            tweet_id = response.data["id"]
            tweet_url = f"https://twitter.com/user/status/{tweet_id}"

            # Get initial metrics
            metrics = await self._get_tweet_metrics(tweet_id)

            return {"post_id": tweet_id, "url": tweet_url, "metrics": metrics}

        except tweepy.TooManyRequests:
            raise RateLimitExceeded("Twitter rate limit exceeded")
        except Exception as e:
            logger.error(f"Twitter posting failed: {e}")
            raise SocialMediaError(f"Twitter posting failed: {e}")

    async def _upload_media(self, media_urls: List[str]) -> List[str]:
        """Upload media files to Twitter"""
        media_ids = []

        for url in media_urls:
            try:
                # Download media
                response = requests.get(url)
                response.raise_for_status()

                # Upload to Twitter
                media = self.client.media_upload(filename=url, file=response.content)
                media_ids.append(media.media_id)

            except Exception as e:
                logger.error(f"Failed to upload media {url}: {e}")

        return media_ids

    async def _get_tweet_metrics(self, tweet_id: str) -> Dict:
        """Get tweet metrics"""
        try:
            tweet = self.client.get_tweet(
                tweet_id, tweet_fields=["public_metrics", "created_at"]
            )

            if tweet.data and tweet.data.public_metrics:
                return {
                    "likes": tweet.data.public_metrics["like_count"],
                    "retweets": tweet.data.public_metrics["retweet_count"],
                    "replies": tweet.data.public_metrics["reply_count"],
                    "quotes": tweet.data.public_metrics["quote_count"],
                    "impressions": tweet.data.public_metrics.get("impression_count", 0),
                }
        except Exception as e:
            logger.error(f"Failed to get tweet metrics: {e}")

        return {}

    def _check_rate_limit(self, user: User) -> bool:
        """Check Twitter rate limits for user"""
        cache_key = f"twitter_rate_limit:{user.id}"
        current_requests = cache.get(cache_key, 0)

        # Twitter allows 300 tweets per 15 minutes
        if current_requests >= 20:  # Conservative limit
            return False

        cache.set(cache_key, current_requests + 1, 900)  # 15 minutes TTL
        return True

    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get detailed analytics for a tweet"""
        return await self._get_tweet_metrics(post_id)


class LinkedInService:
    """LinkedIn API service"""

    def __init__(self):
        self.access_token = settings.LINKEDIN_ACCESS_TOKEN
        self.api_base = "https://api.linkedin.com/v2"

    async def post(
        self, content: str, user: User, media_urls: Optional[List[str]] = None
    ) -> Dict:
        """Post to LinkedIn"""
        if not self.access_token:
            raise SocialMediaError("LinkedIn access token not configured")

        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
            }

            # Get user profile info
            profile_response = requests.get(
                f"{self.api_base}/people/~", headers=headers
            )
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            person_urn = profile_data["id"]

            # Prepare post data
            post_data = {
                "author": f"urn:li:person:{person_urn}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": content},
                        "shareMediaCategory": "NONE",
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            }

            # Post to LinkedIn
            response = requests.post(
                f"{self.api_base}/ugcPosts", headers=headers, json=post_data
            )
            response.raise_for_status()

            post_id = response.headers.get("x-linkedin-id")

            return {
                "post_id": post_id,
                "url": f"https://www.linkedin.com/feed/update/{post_id}",
                "metrics": {},
            }

        except Exception as e:
            logger.error(f"LinkedIn posting failed: {e}")
            raise SocialMediaError(f"LinkedIn posting failed: {e}")

    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get LinkedIn post analytics"""
        # LinkedIn analytics would require additional API calls
        return {}


class FacebookService:
    """Facebook API service"""

    def __init__(self):
        self.access_token = settings.FACEBOOK_ACCESS_TOKEN
        self.page_id = settings.FACEBOOK_PAGE_ID
        self.api_base = "https://graph.facebook.com/v18.0"

    async def post(
        self, content: str, user: User, media_urls: Optional[List[str]] = None
    ) -> Dict:
        """Post to Facebook"""
        if not self.access_token or not self.page_id:
            raise SocialMediaError("Facebook credentials not configured")

        try:
            url = f"{self.api_base}/{self.page_id}/feed"

            data = {"message": content, "access_token": self.access_token}

            response = requests.post(url, data=data)
            response.raise_for_status()

            result = response.json()
            post_id = result["id"]

            return {
                "post_id": post_id,
                "url": f"https://www.facebook.com/{post_id}",
                "metrics": {},
            }

        except Exception as e:
            logger.error(f"Facebook posting failed: {e}")
            raise SocialMediaError(f"Facebook posting failed: {e}")

    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get Facebook post analytics"""
        try:
            url = f"{self.api_base}/{post_id}/insights"
            params = {
                "metric": "post_impressions,post_engaged_users,post_clicks",
                "access_token": self.access_token,
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Failed to get Facebook analytics: {e}")
            return {}


class InstagramService:
    """Instagram API service"""

    def __init__(self):
        self.access_token = settings.INSTAGRAM_ACCESS_TOKEN
        self.account_id = settings.INSTAGRAM_ACCOUNT_ID
        self.api_base = "https://graph.facebook.com/v18.0"

    async def post(
        self, content: str, user: User, media_urls: Optional[List[str]] = None
    ) -> Dict:
        """Post to Instagram"""
        if not self.access_token or not self.account_id:
            raise SocialMediaError("Instagram credentials not configured")

        try:
            # Instagram requires media for posts
            if not media_urls:
                raise SocialMediaError("Instagram posts require media")

            # Create media container
            container_url = f"{self.api_base}/{self.account_id}/media"
            container_data = {
                "image_url": media_urls[0],  # Use first media URL
                "caption": content,
                "access_token": self.access_token,
            }

            container_response = requests.post(container_url, data=container_data)
            container_response.raise_for_status()

            container_id = container_response.json()["id"]

            # Publish the media
            publish_url = f"{self.api_base}/{self.account_id}/media_publish"
            publish_data = {
                "creation_id": container_id,
                "access_token": self.access_token,
            }

            publish_response = requests.post(publish_url, data=publish_data)
            publish_response.raise_for_status()

            post_id = publish_response.json()["id"]

            return {
                "post_id": post_id,
                "url": f"https://www.instagram.com/p/{post_id}",
                "metrics": {},
            }

        except Exception as e:
            logger.error(f"Instagram posting failed: {e}")
            raise SocialMediaError(f"Instagram posting failed: {e}")

    async def get_analytics(self, post_id: str) -> Dict[str, Any]:
        """Get Instagram post analytics"""
        try:
            url = f"{self.api_base}/{post_id}/insights"
            params = {
                "metric": "impressions,reach,likes,comments,shares,saves",
                "access_token": self.access_token,
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"Failed to get Instagram analytics: {e}")
            return {}


# Initialize service
social_media_service = SocialMediaService()
