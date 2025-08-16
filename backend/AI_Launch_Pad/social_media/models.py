import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class SocialMediaAccount(models.Model):
    """Social media accounts connected to the platform"""

    PLATFORM_CHOICES = [
        ("TWITTER", "Twitter/X"),
        ("LINKEDIN", "LinkedIn"),
        ("FACEBOOK", "Facebook"),
        ("INSTAGRAM", "Instagram"),
        ("TELEGRAM", "Telegram"),
        ("DISCORD", "Discord"),
        ("YOUTUBE", "YouTube"),
        ("TIKTOK", "TikTok"),
    ]

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("SUSPENDED", "Suspended"),
        ("ERROR", "Error"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="social_accounts"
    )

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    platform_user_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200, blank=True)

    # Account Details
    profile_picture = models.URLField(blank=True, null=True)
    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)

    # Authentication
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)

    # Settings
    auto_post_enabled = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")

    # Metrics
    total_posts = models.PositiveIntegerField(default=0)
    total_engagement = models.PositiveIntegerField(default=0)
    last_sync = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "social_media_accounts"
        unique_together = ["user", "platform", "platform_user_id"]
        indexes = [
            models.Index(fields=["user", "platform"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.platform})"

    @property
    def is_token_valid(self):
        """Check if access token is still valid"""
        if self.token_expires_at:
            return timezone.now() < self.token_expires_at
        return bool(self.access_token)


class SocialMediaPost(models.Model):
    """Social media posts made through the platform"""

    PLATFORM_CHOICES = [
        ("TWITTER", "Twitter/X"),
        ("LINKEDIN", "LinkedIn"),
        ("FACEBOOK", "Facebook"),
        ("INSTAGRAM", "Instagram"),
        ("TELEGRAM", "Telegram"),
        ("DISCORD", "Discord"),
        ("YOUTUBE", "YouTube"),
        ("TIKTOK", "TikTok"),
    ]

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("SCHEDULED", "Scheduled"),
        ("PUBLISHED", "Published"),
        ("FAILED", "Failed"),
        ("DELETED", "Deleted"),
    ]

    POST_TYPE_CHOICES = [
        ("TEXT", "Text Only"),
        ("IMAGE", "Image"),
        ("VIDEO", "Video"),
        ("LINK", "Link"),
        ("POLL", "Poll"),
        ("STORY", "Story"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="social_posts"
    )
    account = models.ForeignKey(
        SocialMediaAccount,
        on_delete=models.CASCADE,
        related_name="posts",
        null=True,
        blank=True,
    )

    # Post Details
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    post_type = models.CharField(
        max_length=20, choices=POST_TYPE_CHOICES, default="TEXT"
    )
    content = models.TextField()

    # Media
    media_urls = models.JSONField(default=list, help_text="URLs of attached media")
    media_metadata = models.JSONField(
        default=dict, help_text="Media metadata and processing info"
    )

    # Platform Specific
    platform_post_id = models.CharField(max_length=100, blank=True, null=True)
    platform_url = models.URLField(blank=True, null=True)

    # Scheduling
    scheduled_time = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    error_message = models.TextField(blank=True)

    # Engagement Metrics
    metrics = models.JSONField(
        default=dict, help_text="Platform-specific engagement metrics"
    )
    last_metrics_update = models.DateTimeField(null=True, blank=True)

    # AI Generated Content
    is_ai_generated = models.BooleanField(default=False)
    ai_prompt = models.TextField(blank=True)
    ai_agent_used = models.CharField(max_length=100, blank=True)

    # Campaign Association
    campaign_id = models.CharField(
        max_length=100, blank=True, help_text="Associated marketing campaign"
    )

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "social_media_posts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "platform", "status"]),
            models.Index(fields=["scheduled_time"]),
            models.Index(fields=["published_at"]),
            models.Index(fields=["campaign_id"]),
        ]

    def __str__(self):
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return f"{self.platform} - {content_preview}"

    @property
    def engagement_rate(self):
        """Calculate engagement rate from metrics"""
        if not self.metrics or "impressions" not in self.metrics:
            return 0

        impressions = self.metrics.get("impressions", 0)
        if impressions == 0:
            return 0

        # Calculate total engagement based on platform
        if self.platform == "TWITTER":
            engagement = (
                self.metrics.get("likes", 0)
                + self.metrics.get("retweets", 0)
                + self.metrics.get("replies", 0)
                + self.metrics.get("quotes", 0)
            )
        elif self.platform == "LINKEDIN":
            engagement = (
                self.metrics.get("likes", 0)
                + self.metrics.get("comments", 0)
                + self.metrics.get("shares", 0)
            )
        else:
            engagement = sum(
                v
                for k, v in self.metrics.items()
                if k in ["likes", "comments", "shares", "reactions"]
            )

        return (engagement / impressions) * 100 if impressions > 0 else 0


class SocialMediaSchedule(models.Model):
    """Scheduled social media posts"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.OneToOneField(
        SocialMediaPost, on_delete=models.CASCADE, related_name="schedule"
    )

    scheduled_time = models.DateTimeField()
    timezone = models.CharField(max_length=50, default="UTC")

    # Processing Status
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    # Retry Logic
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    next_retry = models.DateTimeField(null=True, blank=True)

    # Error Handling
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "social_media_schedules"
        ordering = ["scheduled_time"]
        indexes = [
            models.Index(fields=["scheduled_time", "is_processed"]),
            models.Index(fields=["next_retry"]),
        ]

    def __str__(self):
        return f"Scheduled: {self.post} at {self.scheduled_time}"


class SocialMediaCampaign(models.Model):
    """Marketing campaigns across social media platforms"""

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("ACTIVE", "Active"),
        ("PAUSED", "Paused"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="social_campaigns"
    )

    # Campaign Details
    name = models.CharField(max_length=200)
    description = models.TextField()

    # Associated Launch
    launch = models.ForeignKey(
        "launches.TokenLaunch",
        on_delete=models.CASCADE,
        related_name="social_campaigns",
        null=True,
        blank=True,
    )

    # Campaign Configuration
    platforms = models.JSONField(default=list, help_text="Target platforms")
    content_templates = models.JSONField(
        default=dict, help_text="Platform-specific content templates"
    )
    posting_schedule = models.JSONField(
        default=dict, help_text="Posting frequency and timing"
    )

    # Budget and Goals
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target_reach = models.PositiveIntegerField(default=0)
    target_engagement = models.PositiveIntegerField(default=0)

    # Status and Timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # AI Configuration
    use_ai_content = models.BooleanField(default=True)
    ai_tone = models.CharField(max_length=50, default="professional")
    ai_guidelines = models.TextField(blank=True)

    # Performance Metrics
    total_posts = models.PositiveIntegerField(default=0)
    total_reach = models.PositiveIntegerField(default=0)
    total_engagement = models.PositiveIntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "social_media_campaigns"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["start_date", "end_date"]),
        ]

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        """Check if campaign is currently active"""
        now = timezone.now()
        return self.status == "ACTIVE" and self.start_date <= now <= self.end_date

    @property
    def engagement_rate(self):
        """Calculate overall engagement rate"""
        if self.total_reach == 0:
            return 0
        return (self.total_engagement / self.total_reach) * 100


class SocialMediaTemplate(models.Model):
    """Reusable content templates"""

    TEMPLATE_TYPE_CHOICES = [
        ("LAUNCH_ANNOUNCEMENT", "Launch Announcement"),
        ("MILESTONE_UPDATE", "Milestone Update"),
        ("COMMUNITY_UPDATE", "Community Update"),
        ("EDUCATIONAL", "Educational Content"),
        ("PROMOTIONAL", "Promotional"),
        ("ENGAGEMENT", "Engagement Post"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_templates"
    )

    name = models.CharField(max_length=200)
    description = models.TextField()
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPE_CHOICES)

    # Template Content
    content_template = models.TextField(help_text="Template with placeholders")
    variables = models.JSONField(
        default=list, help_text="Available variables for substitution"
    )

    # Platform Specific
    platforms = models.JSONField(default=list, help_text="Supported platforms")
    platform_specific_content = models.JSONField(
        default=dict, help_text="Platform-specific variations"
    )

    # Usage and Performance
    usage_count = models.PositiveIntegerField(default=0)
    average_engagement = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Visibility
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "social_media_templates"
        ordering = ["-usage_count", "-created_at"]
        indexes = [
            models.Index(fields=["template_type", "is_public"]),
            models.Index(fields=["is_featured"]),
        ]

    def __str__(self):
        return self.name


class SocialMediaHashtag(models.Model):
    """Trending and suggested hashtags"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tag = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, blank=True)

    # Performance Metrics
    usage_count = models.PositiveIntegerField(default=0)
    trending_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Platform Data
    platform_data = models.JSONField(
        default=dict, help_text="Platform-specific hashtag data"
    )

    # Auto-generated tags
    is_trending = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "social_media_hashtags"
        ordering = ["-trending_score", "-usage_count"]
        indexes = [
            models.Index(fields=["category", "is_trending"]),
            models.Index(fields=["trending_score"]),
        ]

    def __str__(self):
        return f"#{self.tag}"


class SocialMediaAnalytics(models.Model):
    """Daily analytics for social media performance"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="social_analytics"
    )

    date = models.DateField()
    platform = models.CharField(max_length=20, choices=SocialMediaPost.PLATFORM_CHOICES)

    # Content Metrics
    posts_published = models.PositiveIntegerField(default=0)
    total_reach = models.PositiveIntegerField(default=0)
    total_impressions = models.PositiveIntegerField(default=0)
    total_engagement = models.PositiveIntegerField(default=0)

    # Audience Metrics
    followers_gained = models.IntegerField(default=0)
    followers_lost = models.IntegerField(default=0)
    net_follower_change = models.IntegerField(default=0)

    # Performance Metrics
    average_engagement_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    best_posting_time = models.TimeField(null=True, blank=True)

    # Detailed Metrics
    metrics_breakdown = models.JSONField(
        default=dict, help_text="Detailed platform-specific metrics"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "social_media_analytics"
        unique_together = ["user", "date", "platform"]
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["user", "platform", "date"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.platform} analytics for {self.date}"


class SocialMediaWebhook(models.Model):
    """Webhook events from social media platforms"""

    EVENT_TYPE_CHOICES = [
        ("POST_PUBLISHED", "Post Published"),
        ("POST_DELETED", "Post Deleted"),
        ("NEW_FOLLOWER", "New Follower"),
        ("UNFOLLOWER", "Unfollower"),
        ("MENTION", "Mention"),
        ("COMMENT", "Comment"),
        ("LIKE", "Like"),
        ("SHARE", "Share"),
        ("MESSAGE", "Direct Message"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    platform = models.CharField(max_length=20, choices=SocialMediaPost.PLATFORM_CHOICES)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)

    # Event Data
    event_id = models.CharField(max_length=100)
    event_data = models.JSONField(default=dict)
    raw_payload = models.TextField()

    # Processing Status
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    # Associated Records
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(
        SocialMediaPost, on_delete=models.CASCADE, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "social_media_webhooks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["platform", "event_type"]),
            models.Index(fields=["is_processed"]),
            models.Index(fields=["event_id"]),
        ]

    def __str__(self):
        return f"{self.platform} - {self.event_type} ({self.event_id})"
