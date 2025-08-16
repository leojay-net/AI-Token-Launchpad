import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .services import (
    ai_service,
    marketing_agent,
    community_agent,
    analytics_agent,
    launch_guide_agent,
)
from .models import AIAgent, AIInteraction
from core.models import User

logger = logging.getLogger("ai_agents.tasks")


@shared_task(bind=True, max_retries=3)
def generate_ai_content(self, user_id, agent_type, prompt, context=None):
    """Generate AI content asynchronously"""
    try:
        user = User.objects.get(id=user_id)
        agent = AIAgent.objects.get(agent_type=agent_type)

        # Select appropriate service based on agent type
        if agent_type == "MARKETING":
            service = marketing_agent
        elif agent_type == "COMMUNITY":
            service = community_agent
        elif agent_type == "ANALYTICS":
            service = analytics_agent
        elif agent_type == "LAUNCH_GUIDE":
            service = launch_guide_agent
        else:
            service = ai_service

        # Generate content
        result = service.generate_content(
            prompt=prompt, user=user, agent=agent, context=context or {}
        )

        logger.info(f"AI content generated successfully for user {user_id}")
        return result

    except Exception as e:
        logger.error(f"Failed to generate AI content: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))


@shared_task
def generate_social_media_campaign(launch_id, platforms):
    """Generate social media campaign content for a token launch"""
    try:
        from launches.models import TokenLaunch

        launch = TokenLaunch.objects.get(id=launch_id)

        launch_data = {
            "name": launch.name,
            "symbol": launch.symbol,
            "description": launch.description,
            "category": launch.category.name,
            "launch_date": (
                launch.launch_date.isoformat() if launch.launch_date else None
            ),
            "website_url": launch.website_url,
            "twitter_url": launch.twitter_url,
        }

        campaign_results = {}

        for platform in platforms:
            try:
                result = marketing_agent.generate_social_media_post(
                    launch_data=launch_data,
                    platform=platform.lower(),
                    user=launch.creator,
                )
                campaign_results[platform] = result

            except Exception as e:
                logger.error(f"Failed to generate {platform} content: {e}")
                campaign_results[platform] = {"error": str(e)}

        # Store results in launch's AI generated content
        if not launch.ai_generated_content:
            launch.ai_generated_content = {}

        launch.ai_generated_content["social_campaign"] = campaign_results
        launch.save()

        logger.info(f"Social media campaign generated for launch {launch_id}")
        return campaign_results

    except Exception as e:
        logger.error(f"Failed to generate social media campaign: {e}")
        raise


@shared_task
def analyze_launch_performance(launch_id):
    """Analyze token launch performance and provide insights"""
    try:
        from launches.models import TokenLaunch
        from analytics.models import LaunchAnalytics

        launch = TokenLaunch.objects.get(id=launch_id)

        # Gather analytics data
        analytics_data = LaunchAnalytics.objects.filter(
            launch=launch, date__gte=timezone.now().date() - timedelta(days=30)
        )

        # Prepare data for analysis
        data = {
            "launch_info": {
                "name": launch.name,
                "status": launch.status,
                "progress": launch.progress_percentage,
                "funding_progress": float(launch.funding_progress),
                "view_count": launch.view_count,
                "interest_count": launch.interest_count,
            },
            "analytics": [
                {
                    "date": str(analytics.date),
                    "page_views": analytics.page_views,
                    "unique_visitors": analytics.unique_visitors,
                    "conversion_rate": float(analytics.conversion_rate),
                    "social_shares": analytics.social_shares,
                }
                for analytics in analytics_data
            ],
        }

        # Generate insights using analytics agent
        result = analytics_agent.generate_insights(data=data, user=launch.creator)

        # Store insights
        if not launch.ai_generated_content:
            launch.ai_generated_content = {}

        launch.ai_generated_content["performance_insights"] = result
        launch.save()

        logger.info(f"Performance analysis completed for launch {launch_id}")
        return result

    except Exception as e:
        logger.error(f"Failed to analyze launch performance: {e}")
        raise


@shared_task
def provide_launch_guidance(user_id, launch_step, user_data):
    """Provide personalized launch guidance to users"""
    try:
        user = User.objects.get(id=user_id)

        result = launch_guide_agent.provide_guidance(
            step=launch_step, user_data=user_data, user=user
        )

        logger.info(f"Launch guidance provided for user {user_id}, step {launch_step}")
        return result

    except Exception as e:
        logger.error(f"Failed to provide launch guidance: {e}")
        raise


@shared_task
def moderate_community_content(content_id, content_text, user_id):
    """Moderate user-generated content"""
    try:
        user = User.objects.get(id=user_id)

        result = community_agent.moderate_content(content=content_text, user=user)

        # You would update the content based on moderation results
        # This is a placeholder for actual moderation logic

        logger.info(f"Content moderation completed for content {content_id}")
        return result

    except Exception as e:
        logger.error(f"Failed to moderate content: {e}")
        raise


@shared_task
def answer_community_question(question_id, question_text, context, user_id):
    """Answer community questions using AI"""
    try:
        user = User.objects.get(id=user_id)

        result = community_agent.answer_question(
            question=question_text, context=context, user=user
        )

        # You would store the answer in your Q&A system
        # This is a placeholder for actual implementation

        logger.info(f"Community question answered: {question_id}")
        return result

    except Exception as e:
        logger.error(f"Failed to answer community question: {e}")
        raise


@shared_task
def sync_ai_agent_metrics():
    """Sync AI agent performance metrics"""
    try:
        agents = AIAgent.objects.filter(is_active=True)

        for agent in agents:
            # Calculate recent performance metrics
            recent_interactions = AIInteraction.objects.filter(
                agent=agent, created_at__gte=timezone.now() - timedelta(hours=24)
            )

            if recent_interactions.exists():
                # Update success rate
                successful_count = recent_interactions.filter(
                    is_successful=True
                ).count()
                agent.success_rate = (
                    successful_count / recent_interactions.count()
                ) * 100

                # Update average response time
                avg_response_time = recent_interactions.aggregate(
                    avg_time=models.Avg("response_time")
                )["avg_time"]

                if avg_response_time:
                    agent.average_response_time = avg_response_time

                agent.last_active = timezone.now()
                agent.save()

        logger.info("AI agent metrics synced successfully")

    except Exception as e:
        logger.error(f"Failed to sync AI agent metrics: {e}")
        raise


@shared_task
def generate_market_analysis(category, user_id):
    """Generate market analysis for token category"""
    try:
        user = User.objects.get(id=user_id)

        result = marketing_agent.analyze_market_trends(
            token_category=category, user=user
        )

        logger.info(f"Market analysis generated for category {category}")
        return result

    except Exception as e:
        logger.error(f"Failed to generate market analysis: {e}")
        raise


@shared_task
def predict_launch_success(launch_id):
    """Predict success probability for a token launch"""
    try:
        from backend.AI_Launch_Pad.launches.models import TokenLaunch

        launch = TokenLaunch.objects.get(id=launch_id)

        launch_data = {
            "name": launch.name,
            "category": launch.category.name,
            "description": launch.description,
            "funding_goal": float(launch.funding_goal),
            "team_size": len(launch.team_info.get("members", [])),
            "social_presence": bool(launch.twitter_url or launch.telegram_url),
            "has_whitepaper": bool(launch.whitepaper_url),
            "audit_status": len(launch.audit_reports) > 0,
        }

        result = analytics_agent.predict_launch_success(
            launch_data=launch_data, user=launch.creator
        )

        # Store prediction
        if not launch.ai_generated_content:
            launch.ai_generated_content = {}

        launch.ai_generated_content["success_prediction"] = result
        launch.save()

        logger.info(f"Success prediction generated for launch {launch_id}")
        return result

    except Exception as e:
        logger.error(f"Failed to predict launch success: {e}")
        raise


@shared_task
def review_launch_plan(launch_id):
    """Review and provide feedback on launch plan"""
    try:
        from backend.AI_Launch_Pad.launches.models import TokenLaunch

        launch = TokenLaunch.objects.get(id=launch_id)

        plan = {
            "launch_info": {
                "name": launch.name,
                "category": launch.category.name,
                "description": launch.description,
            },
            "timeline": launch.launch_plan.get("timeline", {}),
            "marketing_strategy": launch.marketing_plan,
            "team": launch.team_info,
            "funding": {
                "goal": float(launch.funding_goal),
                "current": float(launch.funding_raised),
            },
        }

        result = launch_guide_agent.review_launch_plan(plan=plan, user=launch.creator)

        # Store review
        if not launch.ai_generated_content:
            launch.ai_generated_content = {}

        launch.ai_generated_content["plan_review"] = result
        launch.save()

        logger.info(f"Launch plan reviewed for launch {launch_id}")
        return result

    except Exception as e:
        logger.error(f"Failed to review launch plan: {e}")
        raise


@shared_task
def batch_content_generation(requests):
    """Process multiple AI content generation requests in batch"""
    try:
        results = []

        for request in requests:
            try:
                result = generate_ai_content.delay(
                    user_id=request["user_id"],
                    agent_type=request["agent_type"],
                    prompt=request["prompt"],
                    context=request.get("context"),
                )
                results.append(
                    {
                        "request_id": request.get("id"),
                        "task_id": result.id,
                        "status": "queued",
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "request_id": request.get("id"),
                        "status": "failed",
                        "error": str(e),
                    }
                )

        logger.info(f"Batch content generation queued: {len(results)} requests")
        return results

    except Exception as e:
        logger.error(f"Failed to process batch content generation: {e}")
        raise


@shared_task
def cleanup_ai_interactions():
    """Clean up old AI interactions to manage storage"""
    try:
        # Keep interactions for 90 days
        cutoff_date = timezone.now() - timedelta(days=90)

        old_interactions = AIInteraction.objects.filter(created_at__lt=cutoff_date)

        count = old_interactions.count()
        old_interactions.delete()

        logger.info(f"Cleaned up {count} old AI interactions")
        return count

    except Exception as e:
        logger.error(f"Failed to cleanup AI interactions: {e}")
        raise
