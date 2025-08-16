import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()


class PlatformAnalytics(models.Model):
    """Overall platform analytics and metrics"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    date = models.DateField(unique=True)

    # User Metrics
    total_users = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    returning_users = models.PositiveIntegerField(default=0)

    # Launch Metrics
    total_launches = models.PositiveIntegerField(default=0)
    new_launches = models.PositiveIntegerField(default=0)
    successful_launches = models.PositiveIntegerField(default=0)
    failed_launches = models.PositiveIntegerField(default=0)

    # Engagement Metrics
    total_sessions = models.PositiveIntegerField(default=0)
    average_session_duration = models.DurationField(null=True, blank=True)
    page_views = models.PositiveIntegerField(default=0)
    bounce_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )

    # AI Agent Metrics
    ai_interactions = models.PositiveIntegerField(default=0)
    ai_tokens_used = models.PositiveIntegerField(default=0)
    ai_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))

    # Social Media Metrics
    social_posts = models.PositiveIntegerField(default=0)
    social_engagement = models.PositiveIntegerField(default=0)
    social_reach = models.PositiveIntegerField(default=0)

    # Revenue Metrics
    total_revenue = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0")
    )
    subscription_revenue = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0")
    )
    transaction_fees = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "platform_analytics"
        ordering = ["-date"]
        verbose_name_plural = "Platform Analytics"

    def __str__(self):
        return f"Platform Analytics - {self.date}"


class UserAnalytics(models.Model):
    """Individual user analytics and behavior tracking"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="analytics")

    date = models.DateField()

    # Activity Metrics
    sessions = models.PositiveIntegerField(default=0)
    session_duration = models.DurationField(null=True, blank=True)
    page_views = models.PositiveIntegerField(default=0)

    # Feature Usage
    launches_created = models.PositiveIntegerField(default=0)
    launches_viewed = models.PositiveIntegerField(default=0)
    ai_interactions = models.PositiveIntegerField(default=0)
    social_posts = models.PositiveIntegerField(default=0)

    # Engagement Metrics
    comments_posted = models.PositiveIntegerField(default=0)
    likes_given = models.PositiveIntegerField(default=0)
    shares_made = models.PositiveIntegerField(default=0)

    # Performance Metrics
    conversion_events = models.PositiveIntegerField(default=0)
    revenue_generated = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_analytics"
        unique_together = ["user", "date"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username} analytics - {self.date}"


class LaunchAnalytics(models.Model):
    """Analytics for individual token launches"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    launch = models.ForeignKey(
        "launches.TokenLaunch",
        on_delete=models.CASCADE,
        related_name="detailed_analytics",
    )

    date = models.DateField()

    # Traffic Metrics
    page_views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    returning_visitors = models.PositiveIntegerField(default=0)

    # Engagement Metrics
    time_on_page = models.DurationField(null=True, blank=True)
    bounce_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )
    scroll_depth = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )

    # Interest and Conversion
    new_interests = models.PositiveIntegerField(default=0)
    conversion_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )

    # Social Metrics
    social_shares = models.PositiveIntegerField(default=0)
    social_mentions = models.PositiveIntegerField(default=0)
    social_reach = models.PositiveIntegerField(default=0)

    # Traffic Sources
    direct_traffic = models.PositiveIntegerField(default=0)
    referral_traffic = models.PositiveIntegerField(default=0)
    social_traffic = models.PositiveIntegerField(default=0)
    search_traffic = models.PositiveIntegerField(default=0)

    # Geographic Data
    top_countries = models.JSONField(default=dict)
    top_cities = models.JSONField(default=dict)

    # Device and Browser Data
    device_breakdown = models.JSONField(default=dict)
    browser_breakdown = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "launch_analytics_detailed"
        unique_together = ["launch", "date"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.launch.name} analytics - {self.date}"


class AIAgentAnalytics(models.Model):
    """Analytics for AI agent usage and performance"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(
        "ai_agents.AIAgent", on_delete=models.CASCADE, related_name="detailed_analytics"
    )

    date = models.DateField()

    # Usage Metrics
    total_interactions = models.PositiveIntegerField(default=0)
    unique_users = models.PositiveIntegerField(default=0)
    average_response_time = models.DecimalField(
        max_digits=8, decimal_places=3, default=Decimal("0")
    )

    # Performance Metrics
    success_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )
    user_satisfaction = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )

    # Cost Metrics
    tokens_used = models.PositiveIntegerField(default=0)
    cost_per_interaction = models.DecimalField(
        max_digits=8, decimal_places=4, default=Decimal("0")
    )
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )

    # Task Breakdown
    task_breakdown = models.JSONField(
        default=dict, help_text="Types of tasks performed"
    )

    # Quality Metrics
    error_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )
    retry_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_agent_analytics"
        unique_together = ["agent", "date"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.agent.name} analytics - {self.date}"


class SocialMediaAnalytics(models.Model):
    """Comprehensive social media analytics"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="social_analytics_detailed"
    )

    date = models.DateField()
    platform = models.CharField(max_length=20)

    # Content Metrics
    posts_published = models.PositiveIntegerField(default=0)
    posts_scheduled = models.PositiveIntegerField(default=0)
    posts_failed = models.PositiveIntegerField(default=0)

    # Reach and Impressions
    total_reach = models.PositiveIntegerField(default=0)
    total_impressions = models.PositiveIntegerField(default=0)
    organic_reach = models.PositiveIntegerField(default=0)
    paid_reach = models.PositiveIntegerField(default=0)

    # Engagement Metrics
    total_likes = models.PositiveIntegerField(default=0)
    total_comments = models.PositiveIntegerField(default=0)
    total_shares = models.PositiveIntegerField(default=0)
    total_clicks = models.PositiveIntegerField(default=0)
    engagement_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )

    # Audience Metrics
    followers_start = models.PositiveIntegerField(default=0)
    followers_end = models.PositiveIntegerField(default=0)
    followers_gained = models.IntegerField(default=0)
    followers_lost = models.IntegerField(default=0)

    # Performance Metrics
    best_post_performance = models.JSONField(default=dict)
    worst_post_performance = models.JSONField(default=dict)
    optimal_posting_times = models.JSONField(default=list)

    # Audience Demographics
    audience_age_breakdown = models.JSONField(default=dict)
    audience_gender_breakdown = models.JSONField(default=dict)
    audience_location_breakdown = models.JSONField(default=dict)

    # Content Analysis
    top_hashtags = models.JSONField(default=list)
    content_type_performance = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "social_media_analytics_detailed"
        unique_together = ["user", "date", "platform"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username} - {self.platform} analytics - {self.date}"


class ConversionFunnel(models.Model):
    """Track conversion funnels for various user journeys"""

    FUNNEL_TYPE_CHOICES = [
        ("REGISTRATION", "User Registration"),
        ("LAUNCH_CREATION", "Launch Creation"),
        ("SOCIAL_CONNECT", "Social Media Connection"),
        ("AI_INTERACTION", "AI Agent Interaction"),
        ("INVESTMENT", "Investment/Purchase"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    funnel_type = models.CharField(max_length=30, choices=FUNNEL_TYPE_CHOICES)
    date = models.DateField()

    # Funnel Steps (customizable based on type)
    step_data = models.JSONField(default=dict, help_text="Step-by-step conversion data")

    # Overall Metrics
    total_entries = models.PositiveIntegerField(default=0)
    total_conversions = models.PositiveIntegerField(default=0)
    conversion_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )

    # Drop-off Analysis
    drop_off_points = models.JSONField(default=dict, help_text="Major drop-off points")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conversion_funnels"
        unique_together = ["funnel_type", "date"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.funnel_type} funnel - {self.date}"


class EventTracking(models.Model):
    """Track custom events throughout the platform"""

    EVENT_CATEGORY_CHOICES = [
        ("USER_ACTION", "User Action"),
        ("SYSTEM_EVENT", "System Event"),
        ("CONVERSION", "Conversion"),
        ("ERROR", "Error"),
        ("PERFORMANCE", "Performance"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Event Details
    category = models.CharField(max_length=20, choices=EVENT_CATEGORY_CHOICES)
    action = models.CharField(max_length=100)
    label = models.CharField(max_length=200, blank=True)

    # Context
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)

    # Event Data
    properties = models.JSONField(default=dict)
    value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    # Technical Details
    url = models.URLField(blank=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "event_tracking"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["category", "action"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.category}: {self.action}"


class PerformanceMetrics(models.Model):
    """System performance and health metrics"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    timestamp = models.DateTimeField(auto_now_add=True)

    # Response Time Metrics
    average_response_time = models.DecimalField(
        max_digits=8, decimal_places=3, default=Decimal("0")
    )
    p95_response_time = models.DecimalField(
        max_digits=8, decimal_places=3, default=Decimal("0")
    )
    p99_response_time = models.DecimalField(
        max_digits=8, decimal_places=3, default=Decimal("0")
    )

    # Error Metrics
    error_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )
    total_errors = models.PositiveIntegerField(default=0)

    # System Metrics
    cpu_usage = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )
    memory_usage = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )
    disk_usage = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )

    # Database Metrics
    db_connections = models.PositiveIntegerField(default=0)
    db_query_time = models.DecimalField(
        max_digits=8, decimal_places=3, default=Decimal("0")
    )
    slow_queries = models.PositiveIntegerField(default=0)

    # External Service Metrics
    ai_service_uptime = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )
    social_media_api_status = models.JSONField(default=dict)

    class Meta:
        db_table = "performance_metrics"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Performance Metrics - {self.timestamp}"


class CohortAnalysis(models.Model):
    """User cohort analysis for retention tracking"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cohort_date = (
        models.DateField()
    )  # When the cohort was created (e.g., registration month)
    period = (
        models.PositiveIntegerField()
    )  # Time period from cohort creation (0, 1, 2, 3... months)

    # Cohort Metrics
    cohort_size = models.PositiveIntegerField(default=0)
    returning_users = models.PositiveIntegerField(default=0)
    retention_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )

    # Engagement Metrics
    active_users = models.PositiveIntegerField(default=0)
    launches_created = models.PositiveIntegerField(default=0)
    ai_interactions = models.PositiveIntegerField(default=0)

    # Revenue Metrics
    revenue_per_user = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )
    total_revenue = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0")
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cohort_analysis"
        unique_together = ["cohort_date", "period"]
        ordering = ["cohort_date", "period"]

    def __str__(self):
        return f"Cohort {self.cohort_date} - Period {self.period}"


class ABTestResult(models.Model):
    """A/B testing results and analysis"""

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("RUNNING", "Running"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    test_name = models.CharField(max_length=200)
    description = models.TextField()

    # Test Configuration
    hypothesis = models.TextField()
    success_metric = models.CharField(max_length=100)

    # Test Variants
    control_variant = models.JSONField(default=dict)
    test_variants = models.JSONField(default=list)

    # Results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    confidence_level = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("95")
    )
    statistical_significance = models.BooleanField(default=False)

    # Metrics
    control_conversion_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )
    test_conversion_rates = models.JSONField(default=dict)

    # Participants
    total_participants = models.PositiveIntegerField(default=0)
    control_participants = models.PositiveIntegerField(default=0)
    test_participants = models.JSONField(default=dict)

    # Timeline
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ab_test_results"
        ordering = ["-created_at"]

    def __str__(self):
        return self.test_name
