import pytest
import uuid
from unittest.mock import Mock, patch, AsyncMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

from social_media.models import (
    SocialMediaAccount,
    SocialMediaPost,
    SocialMediaSchedule,
    SocialMediaCampaign,
    SocialMediaTemplate,
    SocialMediaHashtag,
    SocialMediaAnalytics,
    SocialMediaWebhook,
)
from social_media.services import (
    SocialMediaService,
    TwitterService,
    LinkedInService,
    FacebookService,
    InstagramService,
    SocialMediaError,
    RateLimitExceeded,
)
from social_media.tasks import (
    post_to_social_media,
    process_scheduled_posts,
    update_social_media_metrics,
    generate_campaign_content,
    bulk_schedule_posts,
)

User = get_user_model()


class SocialMediaModelTests(TestCase):
    """Test social media models"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_social_media_account_creation(self):
        """Test social media account creation"""
        account = SocialMediaAccount.objects.create(
            user=self.user,
            platform="TWITTER",
            platform_user_id="123456789",
            username="testuser_twitter",
            display_name="Test User",
            follower_count=1000,
            access_token="test_token",
            auto_post_enabled=True,
        )

        self.assertEqual(account.user, self.user)
        self.assertEqual(account.platform, "TWITTER")
        self.assertEqual(account.username, "testuser_twitter")
        self.assertEqual(account.follower_count, 1000)
        self.assertTrue(account.auto_post_enabled)
        self.assertEqual(account.status, "ACTIVE")

    def test_social_media_post_creation(self):
        """Test social media post creation"""
        post = SocialMediaPost.objects.create(
            user=self.user,
            platform="TWITTER",
            content="This is a test post about #crypto and #blockchain!",
            post_type="TEXT",
            media_urls=["https://example.com/image.jpg"],
            status="DRAFT",
        )

        self.assertEqual(post.user, self.user)
        self.assertEqual(post.platform, "TWITTER")
        self.assertEqual(post.post_type, "TEXT")
        self.assertEqual(len(post.media_urls), 1)
        self.assertEqual(post.status, "DRAFT")

    def test_post_engagement_rate_calculation(self):
        """Test engagement rate calculation"""
        post = SocialMediaPost.objects.create(
            user=self.user,
            platform="TWITTER",
            content="Test post",
            status="PUBLISHED",
            metrics={
                "impressions": 1000,
                "likes": 50,
                "retweets": 10,
                "replies": 5,
                "quotes": 3,
            },
        )

        # For Twitter: (likes + retweets + replies + quotes) / impressions * 100
        expected_rate = (50 + 10 + 5 + 3) / 1000 * 100
        self.assertEqual(post.engagement_rate, expected_rate)

    def test_social_media_schedule_creation(self):
        """Test social media schedule creation"""
        post = SocialMediaPost.objects.create(
            user=self.user,
            platform="TWITTER",
            content="Scheduled post",
            status="SCHEDULED",
            scheduled_time=timezone.now() + timedelta(hours=1),
        )

        schedule = SocialMediaSchedule.objects.create(
            post=post, scheduled_time=post.scheduled_time, timezone="UTC"
        )

        self.assertEqual(schedule.post, post)
        self.assertFalse(schedule.is_processed)
        self.assertEqual(schedule.retry_count, 0)
        self.assertEqual(schedule.max_retries, 3)

    def test_social_media_campaign_creation(self):
        """Test social media campaign creation"""
        campaign = SocialMediaCampaign.objects.create(
            user=self.user,
            name="Token Launch Campaign",
            description="Campaign for new token launch",
            platforms=["TWITTER", "LINKEDIN"],
            content_templates={
                "TWITTER": "Exciting news! {token_name} is launching soon! #{hashtag}",
                "LINKEDIN": "We are proud to announce the launch of {token_name}",
            },
            budget=1000.00,
            target_reach=10000,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            use_ai_content=True,
        )

        self.assertEqual(campaign.user, self.user)
        self.assertEqual(campaign.name, "Token Launch Campaign")
        self.assertEqual(len(campaign.platforms), 2)
        self.assertTrue(campaign.use_ai_content)
        self.assertEqual(float(campaign.budget), 1000.0)

    def test_campaign_is_active_property(self):
        """Test campaign active status property"""
        # Active campaign
        active_campaign = SocialMediaCampaign.objects.create(
            user=self.user,
            name="Active Campaign",
            description="Test campaign",
            status="ACTIVE",
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=1),
        )

        # Inactive campaign (future)
        future_campaign = SocialMediaCampaign.objects.create(
            user=self.user,
            name="Future Campaign",
            description="Test campaign",
            status="ACTIVE",
            start_date=timezone.now() + timedelta(days=1),
            end_date=timezone.now() + timedelta(days=2),
        )

        self.assertTrue(active_campaign.is_active)
        self.assertFalse(future_campaign.is_active)

    def test_social_media_template_creation(self):
        """Test social media template creation"""
        template = SocialMediaTemplate.objects.create(
            creator=self.user,
            name="Launch Announcement Template",
            description="Template for token launch announcements",
            template_type="LAUNCH_ANNOUNCEMENT",
            content_template="🚀 {token_name} ({token_symbol}) is launching on {launch_date}! Join us at {website_url} #crypto #{token_symbol}",
            variables=["token_name", "token_symbol", "launch_date", "website_url"],
            platforms=["TWITTER", "LINKEDIN"],
            is_public=True,
        )

        self.assertEqual(template.creator, self.user)
        self.assertEqual(template.template_type, "LAUNCH_ANNOUNCEMENT")
        self.assertEqual(len(template.variables), 4)
        self.assertTrue(template.is_public)

    def test_hashtag_creation(self):
        """Test hashtag creation and management"""
        hashtag = SocialMediaHashtag.objects.create(
            tag="cryptocurrency",
            category="crypto",
            usage_count=100,
            trending_score=85.5,
            is_trending=True,
            platform_data={
                "twitter": {"volume": 5000, "sentiment": "positive"},
                "linkedin": {"volume": 1200, "sentiment": "neutral"},
            },
        )

        self.assertEqual(hashtag.tag, "cryptocurrency")
        self.assertEqual(hashtag.category, "crypto")
        self.assertTrue(hashtag.is_trending)
        self.assertEqual(float(hashtag.trending_score), 85.5)

    def test_social_media_analytics_creation(self):
        """Test social media analytics creation"""
        analytics = SocialMediaAnalytics.objects.create(
            user=self.user,
            date=timezone.now().date(),
            platform="TWITTER",
            posts_published=5,
            total_reach=10000,
            total_impressions=15000,
            total_engagement=750,
            followers_gained=25,
            followers_lost=5,
            net_follower_change=20,
            average_engagement_rate=5.0,
        )

        self.assertEqual(analytics.user, self.user)
        self.assertEqual(analytics.platform, "TWITTER")
        self.assertEqual(analytics.posts_published, 5)
        self.assertEqual(analytics.net_follower_change, 20)
        self.assertEqual(float(analytics.average_engagement_rate), 5.0)


class SocialMediaServiceTests(TestCase):
    """Test social media service functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.service = SocialMediaService()

    def test_service_initialization(self):
        """Test social media service initialization"""
        self.assertIsNotNone(self.service)
        self.assertIn("twitter", self.service.platforms)
        self.assertIn("linkedin", self.service.platforms)
        self.assertIn("facebook", self.service.platforms)
        self.assertIn("instagram", self.service.platforms)

    @patch("social_media.services.TwitterService.post")
    async def test_post_content_immediately(self, mock_post):
        """Test immediate content posting"""
        mock_post.return_value = {
            "post_id": "123456789",
            "url": "https://twitter.com/user/status/123456789",
            "metrics": {},
        }

        result = await self.service.post_content(
            platform="twitter", content="Test post content", user=self.user
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["platform"], "twitter")
        self.assertEqual(result["post_id"], "123456789")
        mock_post.assert_called_once()

    async def test_post_content_scheduled(self):
        """Test scheduled content posting"""
        future_time = timezone.now() + timedelta(hours=2)

        result = await self.service.post_content(
            platform="twitter",
            content="Scheduled post content",
            user=self.user,
            scheduled_time=future_time,
        )

        self.assertTrue(result["success"])
        self.assertTrue(result["scheduled"])
        self.assertIn("schedule_id", result)

    async def test_post_content_unsupported_platform(self):
        """Test posting to unsupported platform"""
        with pytest.raises(SocialMediaError):
            await self.service.post_content(
                platform="unsupported_platform", content="Test content", user=self.user
            )

    @patch("social_media.services.TwitterService.post")
    async def test_bulk_post(self, mock_post):
        """Test bulk posting functionality"""
        mock_post.return_value = {
            "post_id": "123456789",
            "url": "https://twitter.com/user/status/123456789",
            "metrics": {},
        }

        posts = [
            {"platform": "twitter", "content": "Post 1"},
            {"platform": "twitter", "content": "Post 2"},
            {"platform": "twitter", "content": "Post 3"},
        ]

        # Mock asyncio.sleep to speed up test
        with patch("asyncio.sleep", new_callable=AsyncMock):
            results = await self.service.bulk_post(
                posts=posts, user=self.user, delay_seconds=0.1
            )

        self.assertEqual(len(results), 3)
        self.assertTrue(all(result["success"] for result in results))
        self.assertEqual(mock_post.call_count, 3)


class TwitterServiceTests(TestCase):
    """Test Twitter service functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.twitter_service = TwitterService()

    @patch("social_media.services.tweepy.Client")
    @patch("social_media.services.cache")
    async def test_twitter_post_success(self, mock_cache, mock_client):
        """Test successful Twitter posting"""
        # Mock rate limit check
        mock_cache.get.return_value = 0

        # Mock Twitter client
        mock_response = Mock()
        mock_response.data = {"id": "123456789"}
        mock_client.return_value.create_tweet.return_value = mock_response
        mock_client.return_value.get_tweet.return_value.data.public_metrics = {
            "like_count": 0,
            "retweet_count": 0,
            "reply_count": 0,
            "quote_count": 0,
        }

        self.twitter_service.client = mock_client.return_value

        result = await self.twitter_service.post(
            content="Test tweet content", user=self.user
        )

        self.assertEqual(result["post_id"], "123456789")
        self.assertIn("twitter.com", result["url"])
        mock_client.return_value.create_tweet.assert_called_once()

    @patch("social_media.services.cache")
    async def test_twitter_rate_limit(self, mock_cache):
        """Test Twitter rate limit enforcement"""
        # Mock rate limit exceeded
        mock_cache.get.return_value = 25

        with pytest.raises(RateLimitExceeded):
            await self.twitter_service.post(content="Test tweet", user=self.user)

    def test_twitter_rate_limit_check(self):
        """Test Twitter rate limit checking"""
        with patch("social_media.services.cache") as mock_cache:
            # Within limit
            mock_cache.get.return_value = 5
            result = self.twitter_service._check_rate_limit(self.user)
            self.assertTrue(result)

            # Exceeded limit
            mock_cache.get.return_value = 25
            result = self.twitter_service._check_rate_limit(self.user)
            self.assertFalse(result)


class SocialMediaTaskTests(TestCase):
    """Test social media Celery tasks"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    @patch("social_media.tasks.social_media_service.post_content")
    def test_post_to_social_media_task(self, mock_post):
        """Test social media posting task"""
        mock_post.return_value = {
            "post_id": "123456789",
            "url": "https://twitter.com/user/status/123456789",
        }

        # Create a test post
        post = SocialMediaPost.objects.create(
            user=self.user,
            platform="TWITTER",
            content="Test post for task",
            status="DRAFT",
        )

        # Import and run task directly
        from social_media.tasks import post_to_social_media

        result = post_to_social_media(str(post.id))

        # Verify post was updated
        post.refresh_from_db()
        self.assertEqual(post.status, "PUBLISHED")
        self.assertEqual(post.platform_post_id, "123456789")
        self.assertIsNotNone(post.published_at)

    def test_process_scheduled_posts_task(self):
        """Test scheduled posts processing task"""
        # Create scheduled posts
        past_time = timezone.now() - timedelta(minutes=30)

        # Due post
        due_post = SocialMediaPost.objects.create(
            user=self.user,
            platform="TWITTER",
            content="Due post",
            status="SCHEDULED",
            scheduled_time=past_time,
        )

        due_schedule = SocialMediaSchedule.objects.create(
            post=due_post, scheduled_time=past_time
        )

        # Future post
        future_time = timezone.now() + timedelta(hours=1)
        future_post = SocialMediaPost.objects.create(
            user=self.user,
            platform="TWITTER",
            content="Future post",
            status="SCHEDULED",
            scheduled_time=future_time,
        )

        future_schedule = SocialMediaSchedule.objects.create(
            post=future_post, scheduled_time=future_time
        )

        # Mock the posting task
        with patch("social_media.tasks.post_to_social_media.delay") as mock_task:
            from social_media.tasks import process_scheduled_posts

            result = process_scheduled_posts()

            # Should process 1 due post
            self.assertEqual(result, 1)
            mock_task.assert_called_once_with(str(due_post.id))

            # Check schedule status
            due_schedule.refresh_from_db()
            future_schedule.refresh_from_db()

            self.assertTrue(due_schedule.is_processed)
            self.assertFalse(future_schedule.is_processed)

    def test_bulk_schedule_posts_task(self):
        """Test bulk post scheduling task"""
        posts_data = [
            {
                "platform": "TWITTER",
                "content": "Scheduled post 1",
                "scheduled_time": (timezone.now() + timedelta(hours=1)).isoformat(),
            },
            {
                "platform": "LINKEDIN",
                "content": "Scheduled post 2",
                "scheduled_time": (timezone.now() + timedelta(hours=2)).isoformat(),
                "media_urls": ["https://example.com/image.jpg"],
            },
        ]

        from social_media.tasks import bulk_schedule_posts

        result = bulk_schedule_posts(posts_data, str(self.user.id))

        self.assertEqual(len(result), 2)
        self.assertTrue(all("post_id" in item for item in result))

        # Verify posts were created
        self.assertEqual(SocialMediaPost.objects.count(), 2)
        self.assertEqual(SocialMediaSchedule.objects.count(), 2)

    def test_update_trending_hashtags_task(self):
        """Test trending hashtags update task"""
        from social_media.tasks import update_trending_hashtags

        # Run the task
        result = update_trending_hashtags()

        # Should have created/updated hashtags
        self.assertGreater(result, 0)

        # Verify hashtags were created
        hashtags = SocialMediaHashtag.objects.filter(is_trending=True)
        self.assertGreater(hashtags.count(), 0)

        # Check that crypto-related hashtags were created
        crypto_hashtag = SocialMediaHashtag.objects.filter(tag="crypto").first()
        self.assertIsNotNone(crypto_hashtag)
        self.assertTrue(crypto_hashtag.is_trending)


class SocialMediaIntegrationTests(TestCase):
    """Integration tests for social media system"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create social media account
        self.account = SocialMediaAccount.objects.create(
            user=self.user,
            platform="TWITTER",
            platform_user_id="123456789",
            username="testuser_twitter",
            access_token="test_token",
            auto_post_enabled=True,
        )

    def test_complete_posting_workflow(self):
        """Test complete social media posting workflow"""
        # Create a post
        post = SocialMediaPost.objects.create(
            user=self.user,
            account=self.account,
            platform="TWITTER",
            content="Complete workflow test post #test",
            post_type="TEXT",
            status="DRAFT",
        )

        # Mock the external API call
        with patch("social_media.services.TwitterService.post") as mock_post:
            mock_post.return_value = {
                "post_id": "tweet_123",
                "url": "https://twitter.com/user/status/tweet_123",
                "metrics": {"likes": 0, "retweets": 0, "replies": 0},
            }

            from social_media.tasks import post_to_social_media

            # Execute posting task
            result = post_to_social_media(str(post.id))

            # Verify results
            post.refresh_from_db()
            self.assertEqual(post.status, "PUBLISHED")
            self.assertEqual(post.platform_post_id, "tweet_123")
            self.assertIsNotNone(post.published_at)

    def test_campaign_content_generation_workflow(self):
        """Test campaign content generation workflow"""
        # Create a campaign
        campaign = SocialMediaCampaign.objects.create(
            user=self.user,
            name="Test Campaign",
            description="Test campaign for integration",
            platforms=["TWITTER", "LINKEDIN"],
            content_templates={
                "TWITTER": "Check out our new token! #crypto",
                "LINKEDIN": "We are excited to announce our new project",
            },
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
            use_ai_content=True,
        )

        # Mock AI content generation
        with patch("ai_agents.tasks.generate_ai_content.delay") as mock_ai:
            mock_ai.return_value.id = "task_123"

            from social_media.tasks import generate_campaign_content

            result = generate_campaign_content(str(campaign.id))

            # Should have queued AI generation for each platform
            self.assertEqual(len(result), 2)
            self.assertEqual(mock_ai.call_count, 2)

    def test_analytics_generation_workflow(self):
        """Test analytics generation workflow"""
        # Create some posts with metrics
        yesterday = timezone.now().date() - timedelta(days=1)

        posts = []
        for i in range(3):
            post = SocialMediaPost.objects.create(
                user=self.user,
                platform="TWITTER",
                content=f"Test post {i}",
                status="PUBLISHED",
                published_at=timezone.make_aware(
                    datetime.combine(yesterday, datetime.min.time())
                ),
                metrics={
                    "impressions": 1000 + i * 100,
                    "likes": 50 + i * 10,
                    "retweets": 5 + i,
                    "replies": 2 + i,
                },
            )
            posts.append(post)

        from social_media.tasks import generate_daily_social_analytics

        # Generate analytics
        result = generate_daily_social_analytics()

        # Should have created analytics record
        self.assertGreater(result, 0)

        # Verify analytics were created
        analytics = SocialMediaAnalytics.objects.filter(
            user=self.user, date=yesterday, platform="TWITTER"
        ).first()

        self.assertIsNotNone(analytics)
        self.assertEqual(analytics.posts_published, 3)
        self.assertGreater(analytics.total_impressions, 0)


class SocialMediaPerformanceTests(TestCase):
    """Performance tests for social media system"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_bulk_post_creation_performance(self):
        """Test performance of bulk post creation"""
        import time

        start_time = time.time()

        # Create 100 posts
        posts = []
        for i in range(100):
            posts.append(
                SocialMediaPost(
                    user=self.user,
                    platform="TWITTER",
                    content=f"Bulk post {i} #test",
                    post_type="TEXT",
                    status="DRAFT",
                )
            )

        SocialMediaPost.objects.bulk_create(posts)

        end_time = time.time()
        creation_time = end_time - start_time

        # Should create 100 posts quickly
        self.assertLess(creation_time, 5.0)
        self.assertEqual(SocialMediaPost.objects.count(), 100)

    def test_analytics_query_performance(self):
        """Test performance of analytics queries"""
        import time

        # Create test data
        for i in range(100):
            SocialMediaAnalytics.objects.create(
                user=self.user,
                date=timezone.now().date() - timedelta(days=i),
                platform="TWITTER",
                posts_published=5,
                total_reach=1000,
                total_engagement=100,
            )

        start_time = time.time()

        # Query last 30 days of analytics
        analytics = SocialMediaAnalytics.objects.filter(
            user=self.user, date__gte=timezone.now().date() - timedelta(days=30)
        ).order_by("-date")

        # Force evaluation
        list(analytics)

        end_time = time.time()
        query_time = end_time - start_time

        # Query should be fast
        self.assertLess(query_time, 1.0)


# Pytest fixtures for async testing
@pytest.fixture
def user():
    """Create a test user"""
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def social_account(user):
    """Create a social media account"""
    return SocialMediaAccount.objects.create(
        user=user,
        platform="TWITTER",
        platform_user_id="123456789",
        username="testuser_twitter",
        access_token="test_token",
    )


@pytest.mark.asyncio
async def test_async_social_posting(user, social_account):
    """Test async social media posting"""
    service = SocialMediaService()

    with patch("social_media.services.TwitterService.post") as mock_post:
        mock_post.return_value = {
            "post_id": "123456789",
            "url": "https://twitter.com/user/status/123456789",
            "metrics": {},
        }

        result = await service.post_content(
            platform="twitter", content="Async test post", user=user
        )

        assert result["success"]
        assert result["platform"] == "twitter"


@pytest.mark.asyncio
async def test_async_bulk_posting(user):
    """Test async bulk posting"""
    service = SocialMediaService()

    posts = [
        {"platform": "twitter", "content": f"Async bulk post {i}"} for i in range(3)
    ]

    with patch("social_media.services.TwitterService.post") as mock_post:
        mock_post.return_value = {
            "post_id": "123456789",
            "url": "https://twitter.com/user/status/123456789",
            "metrics": {},
        }

        with patch("asyncio.sleep", new_callable=AsyncMock):
            results = await service.bulk_post(posts=posts, user=user, delay_seconds=0.1)

        assert len(results) == 3
        assert all(result["success"] for result in results)
