import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()


class TokenCategory(models.Model):
    """Categories for token classification"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    icon = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "token_categories"
        verbose_name_plural = "Token Categories"

    def __str__(self):
        return self.name


class LaunchTemplate(models.Model):
    """Pre-defined launch templates for different token types"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(TokenCategory, on_delete=models.CASCADE)

    # Template configuration
    config = models.JSONField(
        default=dict, help_text="Template configuration and default values"
    )

    # Marketing templates
    marketing_templates = models.JSONField(
        default=dict, help_text="Pre-built marketing content templates"
    )

    # Phases and timeline
    phases = models.JSONField(default=list, help_text="Launch phases with timeline")

    # Requirements checklist
    requirements = models.JSONField(
        default=list, help_text="Required items for this template"
    )

    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "launch_templates"

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class TokenLaunch(models.Model):
    """Main model for token launches"""

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("PLANNING", "Planning"),
        ("IN_REVIEW", "In Review"),
        ("APPROVED", "Approved"),
        ("PREPARING", "Preparing"),
        ("LIVE", "Live"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
        ("FAILED", "Failed"),
    ]

    NETWORK_CHOICES = [
        ("ETHEREUM", "Ethereum"),
        ("POLYGON", "Polygon"),
        ("BSC", "Binance Smart Chain"),
        ("ARBITRUM", "Arbitrum"),
        ("OPTIMISM", "Optimism"),
        ("AVALANCHE", "Avalanche"),
        ("SOLANA", "Solana"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic Information
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_launches"
    )
    template = models.ForeignKey(
        LaunchTemplate, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Token Details
    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=20)
    description = models.TextField()
    category = models.ForeignKey(TokenCategory, on_delete=models.CASCADE)

    # Blockchain Details
    network = models.CharField(max_length=20, choices=NETWORK_CHOICES)
    contract_address = models.CharField(max_length=100, blank=True, null=True)

    # Token Economics
    total_supply = models.DecimalField(max_digits=30, decimal_places=0, default=0)
    initial_price = models.DecimalField(
        max_digits=20, decimal_places=8, default=Decimal("0")
    )
    funding_goal = models.DecimalField(
        max_digits=20, decimal_places=8, default=Decimal("0")
    )
    funding_raised = models.DecimalField(
        max_digits=20, decimal_places=8, default=Decimal("0")
    )

    # Launch Configuration
    launch_date = models.DateTimeField(null=True, blank=True)
    presale_start = models.DateTimeField(null=True, blank=True)
    presale_end = models.DateTimeField(null=True, blank=True)

    # Status and Progress
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    progress_percentage = models.PositiveIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Media and Links
    logo_url = models.URLField(blank=True, null=True)
    banner_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    whitepaper_url = models.URLField(blank=True, null=True)

    # Social Media Links
    twitter_url = models.URLField(blank=True, null=True)
    telegram_url = models.URLField(blank=True, null=True)
    discord_url = models.URLField(blank=True, null=True)
    medium_url = models.URLField(blank=True, null=True)

    # Team and Legal
    team_info = models.JSONField(default=dict, help_text="Team member information")
    legal_docs = models.JSONField(default=list, help_text="Legal documentation URLs")
    audit_reports = models.JSONField(default=list, help_text="Security audit reports")

    # Launch Plan
    launch_plan = models.JSONField(
        default=dict, help_text="Detailed launch plan and strategy"
    )
    marketing_plan = models.JSONField(
        default=dict, help_text="Marketing strategy and timeline"
    )

    # AI Generated Content
    ai_generated_content = models.JSONField(
        default=dict, help_text="AI-generated marketing content"
    )

    # Analytics and Metrics
    view_count = models.PositiveIntegerField(default=0)
    interest_count = models.PositiveIntegerField(
        default=0
    )  # Number of users who showed interest
    social_engagement = models.JSONField(
        default=dict, help_text="Social media engagement metrics"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    launched_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "token_launches"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["category", "status"]),
            models.Index(fields=["creator", "status"]),
            models.Index(fields=["launch_date"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    @property
    def is_live(self):
        return self.status == "LIVE"

    @property
    def is_completed(self):
        return self.status in ["COMPLETED", "CANCELLED", "FAILED"]

    @property
    def funding_progress(self):
        if self.funding_goal > 0:
            return min((self.funding_raised / self.funding_goal) * 100, 100)
        return 0

    def update_progress(self):
        """Calculate and update launch progress based on completed tasks"""
        # This would be implemented based on completed launch phases/tasks
        pass


class LaunchPhase(models.Model):
    """Individual phases of a token launch"""

    PHASE_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("SKIPPED", "Skipped"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    launch = models.ForeignKey(
        TokenLaunch, on_delete=models.CASCADE, related_name="phases"
    )

    name = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField()

    # Phase Configuration
    requirements = models.JSONField(
        default=list, help_text="Requirements for this phase"
    )
    deliverables = models.JSONField(default=list, help_text="Expected deliverables")

    # Status and Timing
    status = models.CharField(
        max_length=20, choices=PHASE_STATUS_CHOICES, default="PENDING"
    )
    estimated_duration = models.DurationField(null=True, blank=True)

    # Timestamps
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "launch_phases"
        ordering = ["launch", "order"]
        unique_together = ["launch", "order"]

    def __str__(self):
        return f"{self.launch.name} - {self.name}"


class LaunchTask(models.Model):
    """Individual tasks within launch phases"""

    TASK_STATUS_CHOICES = [
        ("TODO", "To Do"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("BLOCKED", "Blocked"),
        ("CANCELLED", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phase = models.ForeignKey(
        LaunchPhase, on_delete=models.CASCADE, related_name="tasks"
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM"
    )
    status = models.CharField(
        max_length=20, choices=TASK_STATUS_CHOICES, default="TODO"
    )

    # Assignment
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Task Details
    estimated_hours = models.PositiveIntegerField(null=True, blank=True)
    actual_hours = models.PositiveIntegerField(null=True, blank=True)

    # Dependencies
    dependencies = models.ManyToManyField("self", blank=True, symmetrical=False)

    # Attachments and Notes
    attachments = models.JSONField(default=list, help_text="File attachments")
    notes = models.TextField(blank=True)

    # Timestamps
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "launch_tasks"
        ordering = ["phase", "priority", "created_at"]

    def __str__(self):
        return f"{self.phase.name} - {self.title}"


class LaunchComment(models.Model):
    """Comments on launches for feedback and discussions"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    launch = models.ForeignKey(
        TokenLaunch, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()
    is_public = models.BooleanField(default=True)

    # For threaded comments
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "launch_comments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment on {self.launch.name} by {self.author.username}"


class LaunchInterest(models.Model):
    """Track user interest in launches"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    launch = models.ForeignKey(
        TokenLaunch, on_delete=models.CASCADE, related_name="interested_users"
    )

    # Interest Details
    interest_level = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Interest level from 1-5",
    )
    investment_intent = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        null=True,
        blank=True,
        help_text="Intended investment amount",
    )

    # Notifications
    notify_on_launch = models.BooleanField(default=True)
    notify_on_updates = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "launch_interests"
        unique_together = ["user", "launch"]

    def __str__(self):
        return f"{self.user.username} interested in {self.launch.name}"


class LaunchAnalytics(models.Model):
    """Daily analytics for launches"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    launch = models.ForeignKey(
        TokenLaunch, on_delete=models.CASCADE, related_name="analytics"
    )

    date = models.DateField()

    # Traffic Metrics
    page_views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)

    # Engagement Metrics
    new_interests = models.PositiveIntegerField(default=0)
    new_comments = models.PositiveIntegerField(default=0)
    social_shares = models.PositiveIntegerField(default=0)

    # Conversion Metrics
    conversion_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0")
    )

    # Social Media Metrics
    twitter_engagement = models.JSONField(default=dict)
    linkedin_engagement = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "launch_analytics"
        unique_together = ["launch", "date"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.launch.name} analytics for {self.date}"


class LaunchReview(models.Model):
    """Reviews and ratings for completed launches"""

    RATING_CHOICES = [
        (1, "1 Star"),
        (2, "2 Stars"),
        (3, "3 Stars"),
        (4, "4 Stars"),
        (5, "5 Stars"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    launch = models.ForeignKey(
        TokenLaunch, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()

    # Review Categories
    execution_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    communication_rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    innovation_rating = models.PositiveIntegerField(choices=RATING_CHOICES)

    is_verified = models.BooleanField(default=False)  # Verified participant
    is_public = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "launch_reviews"
        unique_together = ["launch", "reviewer"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review of {self.launch.name} by {self.reviewer.username}"


class LaunchMilestone(models.Model):
    """Key milestones in a token launch"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    launch = models.ForeignKey(
        TokenLaunch, on_delete=models.CASCADE, related_name="milestones"
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    target_date = models.DateTimeField()
    achieved_date = models.DateTimeField(null=True, blank=True)

    is_critical = models.BooleanField(default=False)
    is_achieved = models.BooleanField(default=False)

    # Metrics associated with milestone
    target_metrics = models.JSONField(default=dict)
    achieved_metrics = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "launch_milestones"
        ordering = ["target_date"]

    def __str__(self):
        return f"{self.launch.name} - {self.title}"
