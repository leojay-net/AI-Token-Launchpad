from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class AIAgent(models.Model):
    """Base model for AI agents"""

    AGENT_TYPES = [
        ("MARKETING", "Marketing Agent"),
        ("COMMUNITY", "Community Agent"),
        ("ANALYTICS", "Analytics Agent"),
        ("LAUNCH_GUIDE", "Launch Guide Agent"),
    ]

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("MAINTENANCE", "Maintenance"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    agent_type = models.CharField(max_length=20, choices=AGENT_TYPES)
    description = models.TextField()

    # Configuration
    model = models.CharField(max_length=50, default="gemini-pro")
    temperature = models.FloatField(default=0.7)
    max_tokens = models.PositiveIntegerField(default=1000)
    context_limit = models.PositiveIntegerField(default=4000)

    # Status and metrics
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")
    total_interactions = models.PositiveIntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)  # in seconds

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_agent_type_display()})"

    class Meta:
        unique_together = ["name", "agent_type"]


class AIInteraction(models.Model):
    """Track AI agent interactions"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ai_interactions"
    )
    agent = models.ForeignKey(
        AIAgent, on_delete=models.CASCADE, related_name="interactions"
    )

    # Request details
    prompt = models.TextField()
    context = models.JSONField(default=dict)

    # Response details
    response = models.TextField()
    model_used = models.CharField(max_length=50)
    tokens_used = models.PositiveIntegerField(default=0)
    response_time = models.FloatField()  # in seconds
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)

    # Quality metrics
    user_rating = models.PositiveIntegerField(null=True, blank=True)  # 1-5 stars
    feedback = models.TextField(null=True, blank=True)

    # Status
    is_successful = models.BooleanField(default=True)
    error_message = models.TextField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["agent", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.agent.name} at {self.timestamp}"


class AIPromptTemplate(models.Model):
    """Store reusable prompt templates for AI agents"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    agent_type = models.CharField(max_length=20, choices=AIAgent.AGENT_TYPES)
    category = models.CharField(max_length=50)

    # Template content
    template = models.TextField()
    variables = models.JSONField(default=list)  # List of variable names in template

    # Usage and performance
    usage_count = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)

    # Metadata
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_agent_type_display()})"

    class Meta:
        unique_together = ["name", "agent_type"]


class AIConversationContext(models.Model):
    """Manage conversation context for ongoing AI interactions"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ai_contexts")
    agent = models.ForeignKey(
        AIAgent, on_delete=models.CASCADE, related_name="contexts"
    )

    # Context data
    session_id = models.CharField(max_length=100, unique=True)
    conversation_history = models.JSONField(default=list)
    context_data = models.JSONField(default=dict)

    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} -> {self.agent.name} (Session: {self.session_id})"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def add_message(self, role, content):
        """Add a message to conversation history"""
        self.conversation_history.append(
            {"role": role, "content": content, "timestamp": timezone.now().isoformat()}
        )
        self.save()

    def get_recent_messages(self, limit=10):
        """Get recent messages from conversation"""
        return self.conversation_history[-limit:]

    class Meta:
        indexes = [
            models.Index(fields=["user", "agent", "is_active"]),
            models.Index(fields=["expires_at"]),
        ]


class AIAgentMetrics(models.Model):
    """Daily metrics for AI agents"""

    agent = models.ForeignKey(
        AIAgent, on_delete=models.CASCADE, related_name="daily_metrics"
    )
    date = models.DateField()

    # Usage metrics
    total_requests = models.PositiveIntegerField(default=0)
    successful_requests = models.PositiveIntegerField(default=0)
    failed_requests = models.PositiveIntegerField(default=0)

    # Performance metrics
    average_response_time = models.FloatField(default=0.0)
    total_tokens_used = models.PositiveIntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)

    # Quality metrics
    average_user_rating = models.FloatField(default=0.0)
    total_ratings = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["agent", "date"]
        indexes = [
            models.Index(fields=["agent", "date"]),
        ]

    def __str__(self):
        return f"{self.agent.name} - {self.date}"
