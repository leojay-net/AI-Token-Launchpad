import logging
import time
import asyncio
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
import google.generativeai as genai
import openai
from .models import AIAgent, AIInteraction, AIPromptTemplate, AIConversationContext
from core.models import User

logger = logging.getLogger("ai_agents")


class AIServiceError(Exception):
    """Custom exception for AI service errors"""

    pass


class RateLimitExceeded(AIServiceError):
    """Exception raised when rate limit is exceeded"""

    pass


class AIService:
    """Main service for AI interactions"""

    def __init__(self):
        self.setup_clients()
        self.rate_limits = {
            "gemini": {
                "requests_per_minute": settings.GEMINI_RATE_LIMIT_RPM,
                "tokens_per_minute": settings.GEMINI_RATE_LIMIT_TPM,
            }
        }

    def setup_clients(self):
        """Initialize AI service clients"""
        try:
            # Configure Gemini
            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
                logger.info("Gemini client initialized successfully")
            else:
                self.gemini_model = None
                logger.warning("Gemini API key not configured")

            # Configure OpenAI
            if settings.OPENAI_API_KEY:
                openai.api_key = settings.OPENAI_API_KEY
                self.openai_client = openai
                logger.info("OpenAI client initialized successfully")
            else:
                self.openai_client = None
                logger.warning("OpenAI API key not configured")

        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {e}")
            raise AIServiceError(f"AI service initialization failed: {e}")

    def check_rate_limit(self, provider: str, user_id: str) -> bool:
        """Check if user has exceeded rate limits"""
        cache_key = f"rate_limit:{provider}:{user_id}"
        current_requests = cache.get(cache_key, 0)

        if provider in self.rate_limits:
            limit = self.rate_limits[provider]["requests_per_minute"]
            if current_requests >= limit:
                return False

        # Increment counter
        cache.set(cache_key, current_requests + 1, 60)  # 1 minute TTL
        return True

    async def generate_content(
        self,
        prompt: str,
        user: User,
        agent: AIAgent,
        context: Optional[Dict] = None,
        provider: str = "gemini",
    ) -> Dict[str, Any]:
        """Generate content using specified AI provider"""

        start_time = time.time()

        try:
            # Check rate limits
            if not self.check_rate_limit(provider, str(user.id)):
                raise RateLimitExceeded(f"Rate limit exceeded for {provider}")

            # Prepare context
            full_context = self._prepare_context(user, agent, context)

            # Generate content based on provider
            if provider == "gemini" and self.gemini_model:
                result = await self._generate_with_gemini(prompt, full_context, agent)
            elif provider == "openai" and self.openai_client:
                result = await self._generate_with_openai(prompt, full_context, agent)
            else:
                raise AIServiceError(f"Provider {provider} not available")

            response_time = time.time() - start_time

            # Record interaction
            interaction = await self._record_interaction(
                user=user,
                agent=agent,
                prompt=prompt,
                response=result["text"],
                context=full_context,
                provider=provider,
                tokens_used=result.get("tokens_used", 0),
                response_time=response_time,
                cost=result.get("cost", 0),
            )

            return {
                "text": result["text"],
                "interaction_id": interaction.id,
                "response_time": response_time,
                "tokens_used": result.get("tokens_used", 0),
                "cost": result.get("cost", 0),
                "provider": provider,
            }

        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"AI generation failed: {e}")

            # Record failed interaction
            await self._record_interaction(
                user=user,
                agent=agent,
                prompt=prompt,
                response="",
                context=context or {},
                provider=provider,
                response_time=response_time,
                is_successful=False,
                error_message=str(e),
            )

            raise AIServiceError(f"Content generation failed: {e}")

    async def _generate_with_gemini(
        self, prompt: str, context: Dict, agent: AIAgent
    ) -> Dict:
        """Generate content using Gemini"""
        try:
            # Prepare the full prompt with context
            full_prompt = self._format_prompt_with_context(prompt, context)

            # Generate content
            response = await self.gemini_model.generate_content_async(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=agent.temperature,
                    max_output_tokens=agent.max_tokens,
                ),
            )

            # Calculate approximate cost (this would need real pricing)
            tokens_used = len(response.text.split()) * 1.3  # Rough estimation
            cost = (tokens_used / 1000) * 0.0005  # Approximate Gemini pricing

            return {
                "text": response.text,
                "tokens_used": int(tokens_used),
                "cost": cost,
            }

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise

    async def _generate_with_openai(
        self, prompt: str, context: Dict, agent: AIAgent
    ) -> Dict:
        """Generate content using OpenAI"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": f"You are {agent.name}, {agent.description}",
                },
                {"role": "system", "content": f"Context: {context}"},
                {"role": "user", "content": prompt},
            ]

            response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens,
            )

            tokens_used = response.usage.total_tokens
            cost = (tokens_used / 1000) * 0.002  # GPT-3.5-turbo pricing

            return {
                "text": response.choices[0].message.content,
                "tokens_used": tokens_used,
                "cost": cost,
            }

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise

    def _prepare_context(
        self, user: User, agent: AIAgent, additional_context: Optional[Dict]
    ) -> Dict:
        """Prepare context for AI generation"""
        context = {
            "user": {
                "username": user.username,
                "level": user.level,
                "xp": user.xp,
                "wallet_address": user.wallet_address,
            },
            "agent": {
                "name": agent.name,
                "type": agent.agent_type,
                "description": agent.description,
            },
            "timestamp": timezone.now().isoformat(),
        }

        if additional_context:
            context.update(additional_context)

        return context

    def _format_prompt_with_context(self, prompt: str, context: Dict) -> str:
        """Format prompt with context information"""
        context_str = f"Context: {context}\n\n"
        return context_str + prompt

    async def _record_interaction(
        self,
        user: User,
        agent: AIAgent,
        prompt: str,
        response: str,
        context: Dict,
        provider: str,
        tokens_used: int = 0,
        response_time: float = 0,
        cost: float = 0,
        is_successful: bool = True,
        error_message: str = None,
    ) -> AIInteraction:
        """Record AI interaction in database"""

        interaction = AIInteraction.objects.create(
            user=user,
            agent=agent,
            prompt=prompt,
            response=response,
            context=context,
            model_used=provider,
            tokens_used=tokens_used,
            response_time=response_time,
            cost=cost,
            is_successful=is_successful,
            error_message=error_message,
        )

        # Update agent metrics
        agent.total_interactions += 1
        if is_successful:
            # Update average response time
            if agent.average_response_time == 0:
                agent.average_response_time = response_time
            else:
                agent.average_response_time = (
                    agent.average_response_time * (agent.total_interactions - 1)
                    + response_time
                ) / agent.total_interactions

            # Update success rate
            successful_interactions = AIInteraction.objects.filter(
                agent=agent, is_successful=True
            ).count()
            agent.success_rate = (
                successful_interactions / agent.total_interactions
            ) * 100

        agent.last_active = timezone.now()
        agent.save()

        return interaction


class MarketingAgent(AIService):
    """Specialized agent for marketing content generation"""

    async def generate_social_media_post(
        self, launch_data: Dict, platform: str, user: User
    ) -> Dict:
        """Generate social media post for token launch"""
        agent = AIAgent.objects.get(agent_type="MARKETING")

        prompt = self._get_social_media_prompt(launch_data, platform)
        context = {
            "task": "social_media_generation",
            "platform": platform,
            "launch_data": launch_data,
        }

        return await self.generate_content(prompt, user, agent, context)

    async def analyze_market_trends(self, token_category: str, user: User) -> Dict:
        """Analyze market trends for token category"""
        agent = AIAgent.objects.get(agent_type="MARKETING")

        prompt = f"""Analyze current market trends for {token_category} tokens. 
        Provide insights on:
        1. Market sentiment
        2. Key competitors
        3. Opportunities
        4. Recommended marketing strategies
        5. Optimal timing for launch
        
        Be specific and actionable."""

        context = {"task": "market_analysis", "category": token_category}

        return await self.generate_content(prompt, user, agent, context)

    def _get_social_media_prompt(self, launch_data: Dict, platform: str) -> str:
        """Get platform-specific social media prompt"""
        base_info = f"""
        Token Name: {launch_data.get('name')}
        Symbol: {launch_data.get('symbol')}
        Description: {launch_data.get('description')}
        Category: {launch_data.get('category')}
        """

        if platform == "twitter":
            return f"""Create an engaging Twitter post for this token launch:
            {base_info}
            
            Requirements:
            - Under 280 characters
            - Include relevant hashtags
            - Call-to-action
            - Exciting and professional tone
            """
        elif platform == "linkedin":
            return f"""Create a professional LinkedIn post for this token launch:
            {base_info}
            
            Requirements:
            - Professional tone
            - Explain business value
            - Include relevant hashtags
            - Longer format acceptable
            """
        else:
            return f"""Create a social media post for {platform}:
            {base_info}
            
            Make it engaging and appropriate for the platform.
            """


class CommunityAgent(AIService):
    """Specialized agent for community management"""

    async def answer_question(self, question: str, context: Dict, user: User) -> Dict:
        """Answer community questions"""
        agent = AIAgent.objects.get(agent_type="COMMUNITY")

        prompt = f"""As a helpful community manager for AI LaunchPad, answer this question:
        
        Question: {question}
        
        Provide a helpful, accurate, and friendly response. If you don't know something,
        say so and suggest where they might find the answer.
        """

        context.update({"task": "community_qa", "question": question})

        return await self.generate_content(prompt, user, agent, context)

    async def moderate_content(self, content: str, user: User) -> Dict:
        """Moderate user-generated content"""
        agent = AIAgent.objects.get(agent_type="COMMUNITY")

        prompt = f"""Analyze this content for community guidelines violations:
        
        Content: {content}
        
        Check for:
        1. Spam or promotional content
        2. Offensive language
        3. Misinformation
        4. Appropriate topic relevance
        
        Respond with:
        - approved: true/false
        - reasoning: explanation
        - suggestions: improvements if needed
        """

        context = {"task": "content_moderation", "content": content}

        return await self.generate_content(prompt, user, agent, context)


class AnalyticsAgent(AIService):
    """Specialized agent for analytics and insights"""

    async def generate_insights(self, data: Dict, user: User) -> Dict:
        """Generate insights from analytics data"""
        agent = AIAgent.objects.get(agent_type="ANALYTICS")

        prompt = f"""Analyze this platform data and provide actionable insights:
        
        Data: {data}
        
        Provide:
        1. Key trends and patterns
        2. Performance metrics analysis
        3. User behavior insights
        4. Recommendations for improvement
        5. Predictions for future performance
        
        Be specific and data-driven in your analysis.
        """

        context = {"task": "data_analysis", "data_type": "platform_analytics"}

        return await self.generate_content(prompt, user, agent, context)

    async def predict_launch_success(self, launch_data: Dict, user: User) -> Dict:
        """Predict token launch success probability"""
        agent = AIAgent.objects.get(agent_type="ANALYTICS")

        prompt = f"""Analyze this token launch data and predict success probability:
        
        Launch Data: {launch_data}
        
        Consider:
        1. Market conditions
        2. Token utility and uniqueness
        3. Team and community
        4. Marketing strategy
        5. Technical implementation
        
        Provide a success probability score (0-100) with detailed reasoning.
        """

        context = {"task": "launch_prediction", "launch_data": launch_data}

        return await self.generate_content(prompt, user, agent, context)


class LaunchGuideAgent(AIService):
    """Specialized agent for guiding users through token launches"""

    async def provide_guidance(self, step: str, user_data: Dict, user: User) -> Dict:
        """Provide step-by-step launch guidance"""
        agent = AIAgent.objects.get(agent_type="LAUNCH_GUIDE")

        prompt = f"""Provide guidance for the {step} phase of token launch:
        
        User Profile: {user_data}
        
        Give specific, actionable advice including:
        1. What to do in this step
        2. Best practices
        3. Common mistakes to avoid
        4. Tools and resources needed
        5. Success criteria
        
        Tailor advice to user's experience level.
        """

        context = {"task": "launch_guidance", "step": step, "user_data": user_data}

        return await self.generate_content(prompt, user, agent, context)

    async def review_launch_plan(self, plan: Dict, user: User) -> Dict:
        """Review and provide feedback on launch plan"""
        agent = AIAgent.objects.get(agent_type="LAUNCH_GUIDE")

        prompt = f"""Review this token launch plan and provide feedback:
        
        Launch Plan: {plan}
        
        Evaluate:
        1. Completeness of the plan
        2. Feasibility and timeline
        3. Market positioning
        4. Risk assessment
        5. Improvement suggestions
        
        Provide a detailed review with specific recommendations.
        """

        context = {"task": "plan_review", "plan": plan}

        return await self.generate_content(prompt, user, agent, context)


# Initialize service instances
ai_service = AIService()
marketing_agent = MarketingAgent()
community_agent = CommunityAgent()
analytics_agent = AnalyticsAgent()
launch_guide_agent = LaunchGuideAgent()
