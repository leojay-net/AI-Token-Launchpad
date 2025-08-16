import pytest
import uuid
from unittest.mock import Mock, patch, AsyncMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from ai_agents.models import (
    AIAgent,
    AIInteraction,
    AIPromptTemplate,
    AIConversationContext,
)
from ai_agents.services import (
    AIService,
    MarketingAgent,
    CommunityAgent,
    AnalyticsAgent,
    LaunchGuideAgent,
    AIServiceError,
    RateLimitExceeded,
)
from ai_agents.tasks import (
    generate_ai_content,
    generate_social_media_campaign,
    analyze_launch_performance,
    provide_launch_guidance,
)
from core.models import User

User = get_user_model()


class AIAgentModelTests(TestCase):
    """Test AI Agent models"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.agent = AIAgent.objects.create(
            name="Test Marketing Agent",
            agent_type="MARKETING",
            description="Test marketing agent for testing",
            model_provider="gemini",
            model_name="gemini-pro",
            is_active=True,
        )

    def test_agent_creation(self):
        """Test AI agent creation"""
        self.assertEqual(self.agent.name, "Test Marketing Agent")
        self.assertEqual(self.agent.agent_type, "MARKETING")
        self.assertTrue(self.agent.is_active)
        self.assertEqual(self.agent.total_interactions, 0)
        self.assertEqual(self.agent.success_rate, 0)

    def test_agent_string_representation(self):
        """Test agent string representation"""
        expected = f"{self.agent.name} ({self.agent.agent_type})"
        self.assertEqual(str(self.agent), expected)

    def test_interaction_creation(self):
        """Test AI interaction creation"""
        interaction = AIInteraction.objects.create(
            user=self.user,
            agent=self.agent,
            prompt="Test prompt",
            response="Test response",
            context={"test": "context"},
            model_used="gemini-pro",
            tokens_used=100,
            response_time=1.5,
            cost=0.001,
        )

        self.assertEqual(interaction.user, self.user)
        self.assertEqual(interaction.agent, self.agent)
        self.assertEqual(interaction.prompt, "Test prompt")
        self.assertTrue(interaction.is_successful)
        self.assertEqual(interaction.tokens_used, 100)

    def test_prompt_template_creation(self):
        """Test prompt template creation"""
        template = AIPromptTemplate.objects.create(
            name="Test Template",
            template_type="MARKETING",
            template="Hello {name}, welcome to {platform}!",
            variables=["name", "platform"],
            description="Test template for marketing",
        )

        self.assertEqual(template.name, "Test Template")
        self.assertEqual(template.template_type, "MARKETING")
        self.assertEqual(len(template.variables), 2)

    def test_conversation_context_creation(self):
        """Test conversation context creation"""
        context = AIConversationContext.objects.create(
            user=self.user,
            agent=self.agent,
            session_id="test-session-123",
            context_data={"previous_topic": "token launch"},
            message_count=5,
        )

        self.assertEqual(context.user, self.user)
        self.assertEqual(context.agent, self.agent)
        self.assertEqual(context.message_count, 5)


class AIServiceTests(TestCase):
    """Test AI service functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.agent = AIAgent.objects.create(
            name="Test Agent",
            agent_type="MARKETING",
            description="Test agent",
            model_provider="gemini",
            model_name="gemini-pro",
            is_active=True,
        )

        self.ai_service = AIService()

    def test_service_initialization(self):
        """Test AI service initialization"""
        self.assertIsNotNone(self.ai_service)
        # Note: In tests, clients might not be properly initialized due to missing API keys

    @patch("ai_agents.services.cache")
    def test_rate_limit_check(self, mock_cache):
        """Test rate limit checking"""
        # Test within rate limit
        mock_cache.get.return_value = 0
        result = self.ai_service.check_rate_limit("gemini", str(self.user.id))
        self.assertTrue(result)

        # Test exceeded rate limit
        mock_cache.get.return_value = 100
        result = self.ai_service.check_rate_limit("gemini", str(self.user.id))
        self.assertFalse(result)

    @patch("ai_agents.services.genai")
    @patch("ai_agents.services.cache")
    async def test_generate_content_success(self, mock_cache, mock_genai):
        """Test successful content generation"""
        # Mock rate limit check
        mock_cache.get.return_value = 0

        # Mock Gemini response
        mock_response = Mock()
        mock_response.text = "Generated AI content"
        mock_genai.GenerativeModel.return_value.generate_content_async = AsyncMock(
            return_value=mock_response
        )

        result = await self.ai_service.generate_content(
            prompt="Test prompt", user=self.user, agent=self.agent, provider="gemini"
        )

        self.assertIn("text", result)
        self.assertIn("interaction_id", result)
        self.assertEqual(result["provider"], "gemini")

    @patch("ai_agents.services.cache")
    async def test_generate_content_rate_limit(self, mock_cache):
        """Test rate limit exceeded"""
        # Mock rate limit exceeded
        mock_cache.get.return_value = 100

        with pytest.raises(RateLimitExceeded):
            await self.ai_service.generate_content(
                prompt="Test prompt",
                user=self.user,
                agent=self.agent,
                provider="gemini",
            )

    def test_prepare_context(self):
        """Test context preparation"""
        additional_context = {"task": "test_task"}

        context = self.ai_service._prepare_context(
            self.user, self.agent, additional_context
        )

        self.assertIn("user", context)
        self.assertIn("agent", context)
        self.assertIn("timestamp", context)
        self.assertIn("task", context)
        self.assertEqual(context["user"]["username"], self.user.username)
        self.assertEqual(context["agent"]["name"], self.agent.name)


class MarketingAgentTests(TestCase):
    """Test Marketing Agent functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.agent = AIAgent.objects.create(
            name="Marketing Agent",
            agent_type="MARKETING",
            description="Marketing specialist agent",
            model_provider="gemini",
            is_active=True,
        )

        self.marketing_agent = MarketingAgent()

    def test_social_media_prompt_generation(self):
        """Test social media prompt generation"""
        launch_data = {
            "name": "TestCoin",
            "symbol": "TEST",
            "description": "A test cryptocurrency",
            "category": "DeFi",
        }

        prompt = self.marketing_agent._get_social_media_prompt(launch_data, "twitter")

        self.assertIn("TestCoin", prompt)
        self.assertIn("TEST", prompt)
        self.assertIn("280 characters", prompt)
        self.assertIn("hashtags", prompt)

    def test_linkedin_prompt_generation(self):
        """Test LinkedIn-specific prompt generation"""
        launch_data = {
            "name": "TestCoin",
            "symbol": "TEST",
            "description": "A test cryptocurrency",
            "category": "DeFi",
        }

        prompt = self.marketing_agent._get_social_media_prompt(launch_data, "linkedin")

        self.assertIn("TestCoin", prompt)
        self.assertIn("Professional tone", prompt)
        self.assertIn("business value", prompt)

    @patch.object(MarketingAgent, "generate_content")
    async def test_generate_social_media_post(self, mock_generate):
        """Test social media post generation"""
        mock_generate.return_value = {
            "text": "Exciting news! TestCoin is launching soon! #crypto #TestCoin",
            "interaction_id": str(uuid.uuid4()),
            "tokens_used": 50,
        }

        launch_data = {
            "name": "TestCoin",
            "symbol": "TEST",
            "description": "A test cryptocurrency",
        }

        result = await self.marketing_agent.generate_social_media_post(
            launch_data=launch_data, platform="twitter", user=self.user
        )

        self.assertIn("text", result)
        self.assertIn("TestCoin", result["text"])
        mock_generate.assert_called_once()

    @patch.object(MarketingAgent, "generate_content")
    async def test_analyze_market_trends(self, mock_generate):
        """Test market trends analysis"""
        mock_generate.return_value = {
            "text": "DeFi market shows strong growth potential...",
            "interaction_id": str(uuid.uuid4()),
            "tokens_used": 200,
        }

        result = await self.marketing_agent.analyze_market_trends(
            token_category="DeFi", user=self.user
        )

        self.assertIn("text", result)
        self.assertIn("DeFi", result["text"])
        mock_generate.assert_called_once()


class CommunityAgentTests(TestCase):
    """Test Community Agent functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.agent = AIAgent.objects.create(
            name="Community Agent",
            agent_type="COMMUNITY",
            description="Community management agent",
            is_active=True,
        )

        self.community_agent = CommunityAgent()

    @patch.object(CommunityAgent, "generate_content")
    async def test_answer_question(self, mock_generate):
        """Test community question answering"""
        mock_generate.return_value = {
            "text": "Great question! Here's how token launches work...",
            "interaction_id": str(uuid.uuid4()),
            "tokens_used": 100,
        }

        result = await self.community_agent.answer_question(
            question="How do token launches work?",
            context={"topic": "general_help"},
            user=self.user,
        )

        self.assertIn("text", result)
        self.assertIn("question", result["text"])
        mock_generate.assert_called_once()

    @patch.object(CommunityAgent, "generate_content")
    async def test_moderate_content(self, mock_generate):
        """Test content moderation"""
        mock_generate.return_value = {
            "text": '{"approved": true, "reasoning": "Content is appropriate", "suggestions": []}',
            "interaction_id": str(uuid.uuid4()),
            "tokens_used": 75,
        }

        result = await self.community_agent.moderate_content(
            content="This is a helpful post about DeFi protocols", user=self.user
        )

        self.assertIn("text", result)
        mock_generate.assert_called_once()


class AnalyticsAgentTests(TestCase):
    """Test Analytics Agent functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.agent = AIAgent.objects.create(
            name="Analytics Agent",
            agent_type="ANALYTICS",
            description="Data analysis specialist",
            is_active=True,
        )

        self.analytics_agent = AnalyticsAgent()

    @patch.object(AnalyticsAgent, "generate_content")
    async def test_generate_insights(self, mock_generate):
        """Test insights generation"""
        mock_generate.return_value = {
            "text": "Based on the data, user engagement is trending upward...",
            "interaction_id": str(uuid.uuid4()),
            "tokens_used": 150,
        }

        data = {"user_count": 1000, "active_users": 750, "conversion_rate": 5.2}

        result = await self.analytics_agent.generate_insights(data=data, user=self.user)

        self.assertIn("text", result)
        self.assertIn("engagement", result["text"])
        mock_generate.assert_called_once()

    @patch.object(AnalyticsAgent, "generate_content")
    async def test_predict_launch_success(self, mock_generate):
        """Test launch success prediction"""
        mock_generate.return_value = {
            "text": "Success probability: 78% based on market conditions...",
            "interaction_id": str(uuid.uuid4()),
            "tokens_used": 120,
        }

        launch_data = {
            "name": "TestCoin",
            "category": "DeFi",
            "team_size": 5,
            "funding_goal": 100000,
        }

        result = await self.analytics_agent.predict_launch_success(
            launch_data=launch_data, user=self.user
        )

        self.assertIn("text", result)
        self.assertIn("probability", result["text"])
        mock_generate.assert_called_once()


class LaunchGuideAgentTests(TestCase):
    """Test Launch Guide Agent functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.agent = AIAgent.objects.create(
            name="Launch Guide Agent",
            agent_type="LAUNCH_GUIDE",
            description="Token launch guidance specialist",
            is_active=True,
        )

        self.launch_guide = LaunchGuideAgent()

    @patch.object(LaunchGuideAgent, "generate_content")
    async def test_provide_guidance(self, mock_generate):
        """Test launch guidance provision"""
        mock_generate.return_value = {
            "text": "For the planning phase, you should focus on...",
            "interaction_id": str(uuid.uuid4()),
            "tokens_used": 180,
        }

        user_data = {
            "experience_level": "beginner",
            "project_type": "DeFi",
            "team_size": 3,
        }

        result = await self.launch_guide.provide_guidance(
            step="planning", user_data=user_data, user=self.user
        )

        self.assertIn("text", result)
        self.assertIn("planning", result["text"])
        mock_generate.assert_called_once()

    @patch.object(LaunchGuideAgent, "generate_content")
    async def test_review_launch_plan(self, mock_generate):
        """Test launch plan review"""
        mock_generate.return_value = {
            "text": "Your launch plan looks solid. Here are some suggestions...",
            "interaction_id": str(uuid.uuid4()),
            "tokens_used": 200,
        }

        plan = {
            "timeline": "6 months",
            "budget": 50000,
            "marketing_strategy": "Social media focus",
            "team": ["CEO", "CTO", "Marketing Lead"],
        }

        result = await self.launch_guide.review_launch_plan(plan=plan, user=self.user)

        self.assertIn("text", result)
        self.assertIn("plan", result["text"])
        mock_generate.assert_called_once()


class AIAgentTaskTests(TestCase):
    """Test AI agent Celery tasks"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.agent = AIAgent.objects.create(
            name="Test Agent",
            agent_type="MARKETING",
            description="Test agent for tasks",
            is_active=True,
        )

    @patch("ai_agents.tasks.ai_service.generate_content")
    def test_generate_ai_content_task(self, mock_generate):
        """Test AI content generation task"""
        mock_generate.return_value = {
            "text": "Generated content",
            "interaction_id": str(uuid.uuid4()),
            "tokens_used": 100,
        }

        # Note: In real tests, you'd use Celery's test runner
        # For now, we'll test the task function directly
        from ai_agents.tasks import generate_ai_content

        result = generate_ai_content(
            user_id=str(self.user.id),
            agent_type="MARKETING",
            prompt="Test prompt",
            context={"test": "context"},
        )

        self.assertIn("text", result)
        mock_generate.assert_called_once()

    def test_sync_ai_agent_metrics_task(self):
        """Test AI agent metrics sync task"""
        # Create some test interactions
        AIInteraction.objects.create(
            user=self.user,
            agent=self.agent,
            prompt="Test prompt 1",
            response="Test response 1",
            is_successful=True,
            response_time=1.0,
        )

        AIInteraction.objects.create(
            user=self.user,
            agent=self.agent,
            prompt="Test prompt 2",
            response="Test response 2",
            is_successful=False,
            response_time=2.0,
        )

        from ai_agents.tasks import sync_ai_agent_metrics

        # Run the task
        sync_ai_agent_metrics()

        # Check that agent metrics were updated
        self.agent.refresh_from_db()
        self.assertEqual(self.agent.success_rate, 50.0)  # 1 success out of 2


class AIAgentIntegrationTests(TestCase):
    """Integration tests for AI agent system"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create all agent types
        self.agents = {}
        for agent_type in ["MARKETING", "COMMUNITY", "ANALYTICS", "LAUNCH_GUIDE"]:
            self.agents[agent_type] = AIAgent.objects.create(
                name=f"{agent_type.title()} Agent",
                agent_type=agent_type,
                description=f"{agent_type.title()} specialist agent",
                is_active=True,
            )

    def test_all_agents_created(self):
        """Test that all agent types are created"""
        self.assertEqual(len(self.agents), 4)
        self.assertTrue(all(agent.is_active for agent in self.agents.values()))

    def test_agent_interaction_workflow(self):
        """Test complete agent interaction workflow"""
        agent = self.agents["MARKETING"]

        # Create an interaction
        interaction = AIInteraction.objects.create(
            user=self.user,
            agent=agent,
            prompt="Generate a marketing campaign",
            response="Here is your marketing campaign...",
            context={"campaign_type": "social_media"},
            tokens_used=150,
            response_time=2.5,
            cost=0.003,
        )

        self.assertEqual(interaction.user, self.user)
        self.assertEqual(interaction.agent, agent)
        self.assertTrue(interaction.is_successful)

        # Verify interaction is linked correctly
        self.assertIn(interaction, self.user.ai_interactions.all())
        self.assertIn(interaction, agent.interactions.all())

    def test_conversation_context_management(self):
        """Test conversation context management"""
        agent = self.agents["COMMUNITY"]

        # Create conversation context
        context = AIConversationContext.objects.create(
            user=self.user,
            agent=agent,
            session_id="test-session-123",
            context_data={"topic": "token_launch", "step": 1},
            message_count=1,
        )

        # Add more interactions to the conversation
        for i in range(3):
            AIInteraction.objects.create(
                user=self.user,
                agent=agent,
                prompt=f"Question {i+1}",
                response=f"Answer {i+1}",
                context={"session_id": "test-session-123"},
            )

        # Update context
        context.message_count = 4
        context.context_data["step"] = 4
        context.save()

        self.assertEqual(context.message_count, 4)
        self.assertEqual(context.context_data["step"], 4)


# Pytest fixtures for async testing
@pytest.fixture
def user():
    """Create a test user"""
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def marketing_agent():
    """Create a marketing agent"""
    return AIAgent.objects.create(
        name="Marketing Agent",
        agent_type="MARKETING",
        description="Marketing specialist",
        is_active=True,
    )


@pytest.mark.asyncio
async def test_async_content_generation(user, marketing_agent):
    """Test async content generation with pytest-asyncio"""
    service = MarketingAgent()

    with patch.object(service, "generate_content") as mock_generate:
        mock_generate.return_value = {
            "text": "Generated marketing content",
            "interaction_id": str(uuid.uuid4()),
            "tokens_used": 100,
        }

        result = await service.generate_social_media_post(
            launch_data={"name": "TestCoin", "symbol": "TEST"},
            platform="twitter",
            user=user,
        )

        assert "text" in result
        assert "TestCoin" in result["text"] or "marketing content" in result["text"]


# Performance tests
class AIAgentPerformanceTests(TestCase):
    """Performance tests for AI agent system"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.agent = AIAgent.objects.create(
            name="Performance Test Agent",
            agent_type="MARKETING",
            description="Agent for performance testing",
            is_active=True,
        )

    def test_bulk_interaction_creation(self):
        """Test creating many interactions efficiently"""
        import time

        start_time = time.time()

        # Create 100 interactions
        interactions = []
        for i in range(100):
            interactions.append(
                AIInteraction(
                    user=self.user,
                    agent=self.agent,
                    prompt=f"Test prompt {i}",
                    response=f"Test response {i}",
                    tokens_used=50,
                    response_time=1.0,
                )
            )

        AIInteraction.objects.bulk_create(interactions)

        end_time = time.time()
        creation_time = end_time - start_time

        # Should create 100 interactions in reasonable time
        self.assertLess(creation_time, 5.0)  # Less than 5 seconds
        self.assertEqual(AIInteraction.objects.count(), 100)

    def test_agent_metrics_calculation_performance(self):
        """Test performance of agent metrics calculation"""
        import time

        # Create many interactions
        interactions = []
        for i in range(1000):
            interactions.append(
                AIInteraction(
                    user=self.user,
                    agent=self.agent,
                    prompt=f"Test prompt {i}",
                    response=f"Test response {i}",
                    is_successful=(i % 2 == 0),  # 50% success rate
                    response_time=1.0 + (i % 10) * 0.1,  # Varying response times
                    tokens_used=50 + (i % 20),
                )
            )

        AIInteraction.objects.bulk_create(interactions)

        start_time = time.time()

        # Calculate metrics (this would be part of the sync task)
        recent_interactions = AIInteraction.objects.filter(agent=self.agent)
        successful_count = recent_interactions.filter(is_successful=True).count()
        success_rate = (successful_count / recent_interactions.count()) * 100

        end_time = time.time()
        calculation_time = end_time - start_time

        # Metrics calculation should be fast
        self.assertLess(calculation_time, 1.0)  # Less than 1 second
        self.assertEqual(success_rate, 50.0)  # Expected 50% success rate
