from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class User(AbstractUser):
    """Extended User model for AI LaunchPad platform"""

    # Unique identifier
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Blockchain/Web3 identifiers
    wallet_address = models.CharField(max_length=42, unique=True, null=True, blank=True)

    # Profile information
    avatar = models.URLField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(null=True, blank=True)

    # Social connections
    twitter_handle = models.CharField(max_length=15, null=True, blank=True)
    discord_id = models.CharField(max_length=20, null=True, blank=True)
    telegram_id = models.CharField(max_length=20, null=True, blank=True)

    # Gamification
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    streak = models.PositiveIntegerField(default=0)
    last_active = models.DateTimeField(default=timezone.now)

    # Preferences
    email_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    ai_agent_notifications = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} (Level {self.level})"

    def calculate_next_level_xp(self):
        """Calculate XP needed for next level"""
        return self.level * 1000

    def add_xp(self, amount):
        """Add XP and handle level ups"""
        self.xp += amount
        while self.xp >= self.calculate_next_level_xp():
            self.xp -= self.calculate_next_level_xp()
            self.level += 1
        self.save()


class Achievement(models.Model):
    """Achievement system for gamification"""

    RARITY_CHOICES = [
        ("COMMON", "Common"),
        ("RARE", "Rare"),
        ("EPIC", "Epic"),
        ("LEGENDARY", "Legendary"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)  # Icon identifier
    rarity = models.CharField(max_length=10, choices=RARITY_CHOICES)
    category = models.CharField(max_length=50)

    # Requirements (stored as JSON)
    requirements = models.JSONField(default=dict)
    xp_reward = models.PositiveIntegerField()

    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.rarity})"


class UserAchievement(models.Model):
    """Many-to-many relationship for user achievements"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="achievements"
    )
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    progress = models.JSONField(default=dict)  # Track progress towards achievement

    class Meta:
        unique_together = ["user", "achievement"]

    def __str__(self):
        return f"{self.user.username} - {self.achievement.title}"


class APIUsage(models.Model):
    """Track API usage for rate limiting and billing"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_usage")
    endpoint = models.CharField(max_length=100)
    method = models.CharField(max_length=10)

    # Request details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()

    # Response details
    status_code = models.PositiveIntegerField()
    response_time = models.FloatField()  # in milliseconds

    # Billing
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["endpoint", "timestamp"]),
        ]


class SystemConfiguration(models.Model):
    """System-wide configuration settings"""

    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(null=True, blank=True)

    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value[:50]}"

    @classmethod
    def get_value(cls, key, default=None):
        """Get configuration value by key"""
        try:
            config = cls.objects.get(key=key, is_active=True)
            return config.value
        except cls.DoesNotExist:
            return default


class Web3Nonce(models.Model):
    """Temporary nonce storage for Web3 signature login"""

    address = models.CharField(max_length=42, unique=True)
    nonce = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "web3_nonces"
        indexes = [
            models.Index(fields=["address", "created_at"]),
        ]
