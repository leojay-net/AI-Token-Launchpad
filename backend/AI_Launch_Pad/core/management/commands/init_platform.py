import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

from ai_agents.models import AIAgent, AIPromptTemplate
from backend.AI_Launch_Pad.launches.models import TokenCategory, LaunchTemplate
from social_media.models import SocialMediaHashtag, SocialMediaTemplate
from core.models import Achievement

User = get_user_model()


class Command(BaseCommand):
    """Initialize AI LaunchPad with default data"""

    help = "Initialize AI LaunchPad platform with default agents, templates, and categories"

    def add_arguments(self, parser):
        parser.add_argument(
            "--create-superuser",
            action="store_true",
            help="Create a superuser account",
        )
        parser.add_argument(
            "--superuser-email",
            type=str,
            default="admin@ailaunchpad.com",
            help="Email for superuser account",
        )
        parser.add_argument(
            "--superuser-username",
            type=str,
            default="admin",
            help="Username for superuser account",
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("🚀 Initializing AI LaunchPad Platform...")
        )

        with transaction.atomic():
            # Initialize AI Agents
            self.create_ai_agents()

            # Initialize Token Categories
            self.create_token_categories()

            # Initialize Launch Templates
            self.create_launch_templates()

            # Initialize AI Prompt Templates
            self.create_prompt_templates()

            # Initialize Social Media Templates
            self.create_social_media_templates()

            # Initialize Default Hashtags
            self.create_default_hashtags()

            # Initialize Achievements
            self.create_achievements()

            # Create superuser if requested
            if options["create_superuser"]:
                self.create_superuser(
                    options["superuser_username"], options["superuser_email"]
                )

        self.stdout.write(
            self.style.SUCCESS("✅ AI LaunchPad Platform initialized successfully!")
        )

    def create_ai_agents(self):
        """Create default AI agents"""
        self.stdout.write("Creating AI Agents...")

        agents_data = [
            {
                "name": "Marketing Specialist",
                "agent_type": "MARKETING",
                "description": "Expert in token marketing, social media campaigns, and market analysis. Helps create compelling content and marketing strategies.",
                "system_prompt": "You are a cryptocurrency marketing expert with deep knowledge of token launches, social media marketing, and market analysis. Provide strategic, actionable marketing advice.",
                "model_provider": "gemini",
                "model_name": "gemini-pro",
                "temperature": 0.7,
                "max_tokens": 1000,
                "is_active": True,
            },
            {
                "name": "Community Manager",
                "agent_type": "COMMUNITY",
                "description": "Manages community interactions, answers questions, and moderates content. Builds engagement and handles user support.",
                "system_prompt": "You are a friendly and knowledgeable community manager for a token launchpad platform. Help users with questions, provide guidance, and maintain a positive community environment.",
                "model_provider": "gemini",
                "model_name": "gemini-pro",
                "temperature": 0.6,
                "max_tokens": 800,
                "is_active": True,
            },
            {
                "name": "Analytics Expert",
                "agent_type": "ANALYTICS",
                "description": "Analyzes platform data, generates insights, and predicts launch success. Provides data-driven recommendations.",
                "system_prompt": "You are a data analytics expert specializing in cryptocurrency and token launch metrics. Analyze data objectively and provide actionable insights.",
                "model_provider": "gemini",
                "model_name": "gemini-pro",
                "temperature": 0.3,
                "max_tokens": 1200,
                "is_active": True,
            },
            {
                "name": "Launch Guide",
                "agent_type": "LAUNCH_GUIDE",
                "description": "Provides step-by-step guidance through token launch process. Offers personalized advice based on project needs.",
                "system_prompt": "You are an experienced token launch consultant. Guide users through each phase of their token launch with detailed, practical advice tailored to their experience level.",
                "model_provider": "gemini",
                "model_name": "gemini-pro",
                "temperature": 0.5,
                "max_tokens": 1500,
                "is_active": True,
            },
        ]

        for agent_data in agents_data:
            agent, created = AIAgent.objects.get_or_create(
                agent_type=agent_data["agent_type"], defaults=agent_data
            )
            if created:
                self.stdout.write(f"  ✓ Created agent: {agent.name}")
            else:
                self.stdout.write(f"  - Agent already exists: {agent.name}")

    def create_token_categories(self):
        """Create default token categories"""
        self.stdout.write("Creating Token Categories...")

        categories_data = [
            {
                "name": "DeFi",
                "slug": "defi",
                "description": "Decentralized Finance protocols and applications",
                "icon": "💰",
            },
            {
                "name": "NFT",
                "slug": "nft",
                "description": "Non-Fungible Tokens and digital collectibles",
                "icon": "🎨",
            },
            {
                "name": "Gaming",
                "slug": "gaming",
                "description": "Blockchain-based games and gaming tokens",
                "icon": "🎮",
            },
            {
                "name": "Infrastructure",
                "slug": "infrastructure",
                "description": "Blockchain infrastructure and developer tools",
                "icon": "🔧",
            },
            {
                "name": "Social",
                "slug": "social",
                "description": "Social networks and community platforms",
                "icon": "👥",
            },
            {
                "name": "Metaverse",
                "slug": "metaverse",
                "description": "Virtual worlds and metaverse projects",
                "icon": "🌐",
            },
            {
                "name": "AI",
                "slug": "ai",
                "description": "Artificial Intelligence and machine learning",
                "icon": "🤖",
            },
            {
                "name": "Utility",
                "slug": "utility",
                "description": "Utility tokens for various services",
                "icon": "⚡",
            },
        ]

        for category_data in categories_data:
            category, created = TokenCategory.objects.get_or_create(
                slug=category_data["slug"], defaults=category_data
            )
            if created:
                self.stdout.write(f"  ✓ Created category: {category.name}")
            else:
                self.stdout.write(f"  - Category already exists: {category.name}")

    def create_launch_templates(self):
        """Create default launch templates"""
        self.stdout.write("Creating Launch Templates...")

        # Get categories for templates
        defi_category = TokenCategory.objects.get(slug="defi")
        nft_category = TokenCategory.objects.get(slug="nft")
        gaming_category = TokenCategory.objects.get(slug="gaming")

        templates_data = [
            {
                "name": "DeFi Protocol Launch",
                "description": "Complete template for launching a DeFi protocol with yield farming and governance features",
                "category": defi_category,
                "config": {
                    "default_supply": "1000000000",
                    "suggested_price": "0.01",
                    "launch_phases": [
                        "Planning",
                        "Development",
                        "Audit",
                        "Marketing",
                        "Launch",
                    ],
                    "required_documents": ["Whitepaper", "Tokenomics", "Audit Report"],
                },
                "marketing_templates": {
                    "announcement": "Introducing {token_name} - The next generation DeFi protocol",
                    "features": "Key features: Yield farming, Governance, Cross-chain compatibility",
                    "timeline": "Launch timeline: Q{quarter} {year}",
                },
                "phases": [
                    {
                        "name": "Planning",
                        "duration": 30,
                        "description": "Project planning and team assembly",
                    },
                    {
                        "name": "Development",
                        "duration": 90,
                        "description": "Smart contract development",
                    },
                    {
                        "name": "Audit",
                        "duration": 30,
                        "description": "Security audit and testing",
                    },
                    {
                        "name": "Marketing",
                        "duration": 45,
                        "description": "Marketing campaign and community building",
                    },
                    {
                        "name": "Launch",
                        "duration": 15,
                        "description": "Token launch and listing",
                    },
                ],
                "requirements": [
                    "Smart contract code",
                    "Security audit",
                    "Whitepaper",
                    "Team verification",
                    "Legal compliance",
                ],
            },
            {
                "name": "NFT Collection Launch",
                "description": "Template for launching NFT collections with utility and roadmap",
                "category": nft_category,
                "config": {
                    "collection_size": "10000",
                    "mint_price": "0.1",
                    "launch_phases": [
                        "Concept",
                        "Art Creation",
                        "Smart Contract",
                        "Marketing",
                        "Mint",
                    ],
                    "required_documents": [
                        "Roadmap",
                        "Art Samples",
                        "Utility Description",
                    ],
                },
                "marketing_templates": {
                    "announcement": "Unique NFT collection: {collection_name} - {collection_size} unique pieces",
                    "features": "Exclusive utilities, community access, and future roadmap",
                    "mint_info": "Mint starts {mint_date} at {mint_price} ETH",
                },
                "phases": [
                    {
                        "name": "Concept",
                        "duration": 14,
                        "description": "Collection concept and planning",
                    },
                    {
                        "name": "Art Creation",
                        "duration": 60,
                        "description": "Artwork creation and metadata",
                    },
                    {
                        "name": "Smart Contract",
                        "duration": 21,
                        "description": "Contract development and testing",
                    },
                    {
                        "name": "Marketing",
                        "duration": 30,
                        "description": "Community building and promotion",
                    },
                    {
                        "name": "Mint",
                        "duration": 7,
                        "description": "Public mint and launch",
                    },
                ],
            },
            {
                "name": "Gaming Token Launch",
                "description": "Template for gaming tokens with play-to-earn mechanics",
                "category": gaming_category,
                "config": {
                    "default_supply": "500000000",
                    "game_integration": True,
                    "staking_rewards": True,
                    "required_documents": [
                        "Game Design Document",
                        "Tokenomics",
                        "Roadmap",
                    ],
                },
                "marketing_templates": {
                    "announcement": "{token_name} - The gaming token that rewards players",
                    "features": "Play-to-earn, Staking rewards, In-game utility",
                    "game_info": "Integrated with {game_name} - launching {launch_date}",
                },
            },
        ]

        for template_data in templates_data:
            template, created = LaunchTemplate.objects.get_or_create(
                name=template_data["name"], defaults=template_data
            )
            if created:
                self.stdout.write(f"  ✓ Created template: {template.name}")
            else:
                self.stdout.write(f"  - Template already exists: {template.name}")

    def create_prompt_templates(self):
        """Create AI prompt templates"""
        self.stdout.write("Creating AI Prompt Templates...")

        templates_data = [
            {
                "name": "Social Media Post Generator",
                "template_type": "MARKETING",
                "template": """Create a {platform} post for {token_name} ({token_symbol}):

Project: {description}
Category: {category}
Launch Date: {launch_date}
Target Audience: {target_audience}

Requirements:
- Engaging and professional tone
- Include relevant hashtags
- Call-to-action
- Platform-appropriate length
- Highlight key benefits

Generate an exciting post that drives engagement and interest.""",
                "variables": [
                    "platform",
                    "token_name",
                    "token_symbol",
                    "description",
                    "category",
                    "launch_date",
                    "target_audience",
                ],
                "description": "Generate platform-specific social media posts for token launches",
            },
            {
                "name": "Market Analysis Generator",
                "template_type": "ANALYTICS",
                "template": """Analyze the {category} market for {token_name}:

Current Market Data:
- Market Cap: {market_cap}
- Active Projects: {active_projects}
- Recent Trends: {trends}

Analysis Requirements:
1. Market sentiment and trends
2. Competitive landscape
3. Opportunities and threats
4. Timing recommendations
5. Strategic positioning advice

Provide actionable insights for optimal market entry.""",
                "variables": [
                    "category",
                    "token_name",
                    "market_cap",
                    "active_projects",
                    "trends",
                ],
                "description": "Generate comprehensive market analysis reports",
            },
            {
                "name": "Community Question Handler",
                "template_type": "COMMUNITY",
                "template": """Answer this community question about {platform_name}:

Question: {question}
User Level: {user_level}
Context: {context}

Guidelines:
- Be helpful and informative
- Use simple language for beginners
- Provide specific examples
- Include relevant links if helpful
- Maintain friendly, professional tone

If uncertain, direct to appropriate resources or team members.""",
                "variables": ["platform_name", "question", "user_level", "context"],
                "description": "Handle community questions with appropriate context",
            },
            {
                "name": "Launch Phase Guidance",
                "template_type": "LAUNCH_GUIDE",
                "template": """Provide guidance for the {phase_name} phase:

Project Details:
- Token: {token_name}
- Category: {category}
- Team Size: {team_size}
- Experience Level: {experience_level}
- Timeline: {timeline}

Phase Requirements:
{phase_requirements}

Provide detailed, step-by-step guidance including:
1. Key tasks and milestones
2. Best practices and tips
3. Common pitfalls to avoid
4. Required resources and tools
5. Success criteria and checkpoints

Tailor advice to the team's experience level.""",
                "variables": [
                    "phase_name",
                    "token_name",
                    "category",
                    "team_size",
                    "experience_level",
                    "timeline",
                    "phase_requirements",
                ],
                "description": "Provide detailed guidance for specific launch phases",
            },
        ]

        for template_data in templates_data:
            template, created = AIPromptTemplate.objects.get_or_create(
                name=template_data["name"], defaults=template_data
            )
            if created:
                self.stdout.write(f"  ✓ Created prompt template: {template.name}")
            else:
                self.stdout.write(
                    f"  - Prompt template already exists: {template.name}"
                )

    def create_social_media_templates(self):
        """Create social media templates"""
        self.stdout.write("Creating Social Media Templates...")

        templates_data = [
            {
                "name": "Token Launch Announcement",
                "template_type": "LAUNCH_ANNOUNCEMENT",
                "description": "Announce new token launches across platforms",
                "content_template": "🚀 Exciting news! {token_name} ({token_symbol}) is launching {launch_date}!\n\n✨ {key_features}\n🌐 Learn more: {website_url}\n\n#{token_symbol} #crypto #tokenlaunch #blockchain",
                "variables": [
                    "token_name",
                    "token_symbol",
                    "launch_date",
                    "key_features",
                    "website_url",
                ],
                "platforms": ["TWITTER", "LINKEDIN", "FACEBOOK"],
                "platform_specific_content": {
                    "TWITTER": "🚀 {token_name} ({token_symbol}) launches {launch_date}!\n\n✨ {key_features}\n🌐 {website_url}\n\n#{token_symbol} #crypto #DeFi",
                    "LINKEDIN": "We are excited to announce the launch of {token_name} ({token_symbol}) on {launch_date}.\n\nKey features:\n{key_features}\n\nLearn more about our innovative approach: {website_url}\n\n#blockchain #cryptocurrency #innovation",
                    "FACEBOOK": "🎉 Big announcement! {token_name} is launching {launch_date}!\n\n{key_features}\n\nJoin our community and learn more at {website_url}\n\n#{token_symbol} #cryptocurrency #blockchain",
                },
                "is_public": True,
                "is_featured": True,
            },
            {
                "name": "Milestone Achievement",
                "template_type": "MILESTONE_UPDATE",
                "description": "Celebrate project milestones and achievements",
                "content_template": "🎯 Milestone achieved! {milestone_name}\n\n📊 Progress: {progress_details}\n👥 Community: {community_stats}\n🔜 Next: {next_milestone}\n\nThank you for your continued support! 🙏\n\n#{token_symbol} #milestone #crypto",
                "variables": [
                    "milestone_name",
                    "progress_details",
                    "community_stats",
                    "next_milestone",
                    "token_symbol",
                ],
                "platforms": ["TWITTER", "LINKEDIN", "TELEGRAM"],
                "is_public": True,
            },
            {
                "name": "Community Engagement",
                "template_type": "ENGAGEMENT",
                "description": "Drive community engagement and interaction",
                "content_template": "💭 Question for our amazing community:\n\n{question}\n\nDrop your thoughts below! 👇\n\nBest answer gets {reward}! 🎁\n\n#{token_symbol} #community #crypto #engagement",
                "variables": ["question", "reward", "token_symbol"],
                "platforms": ["TWITTER", "DISCORD", "TELEGRAM"],
                "is_public": True,
            },
            {
                "name": "Educational Content",
                "template_type": "EDUCATIONAL",
                "description": "Share educational content about crypto and blockchain",
                "content_template": "📚 Did you know?\n\n{educational_topic}\n\n{explanation}\n\n{additional_resources}\n\nShare this knowledge! 🔄\n\n#education #crypto #blockchain #learning",
                "variables": [
                    "educational_topic",
                    "explanation",
                    "additional_resources",
                ],
                "platforms": ["TWITTER", "LINKEDIN", "MEDIUM"],
                "is_public": True,
            },
        ]

        for template_data in templates_data:
            # Create user for system templates (use superuser if exists)
            creator = User.objects.filter(is_superuser=True).first()
            if not creator:
                creator = User.objects.create_user(
                    username="system", email="system@ailaunchpad.com", is_staff=True
                )

            template_data["creator"] = creator
            template, created = SocialMediaTemplate.objects.get_or_create(
                name=template_data["name"], defaults=template_data
            )
            if created:
                self.stdout.write(f"  ✓ Created social template: {template.name}")
            else:
                self.stdout.write(
                    f"  - Social template already exists: {template.name}"
                )

    def create_default_hashtags(self):
        """Create default trending hashtags"""
        self.stdout.write("Creating Default Hashtags...")

        hashtags_data = [
            # Crypto General
            {"tag": "crypto", "category": "general", "trending_score": 95.0},
            {"tag": "blockchain", "category": "general", "trending_score": 90.0},
            {"tag": "cryptocurrency", "category": "general", "trending_score": 85.0},
            {"tag": "bitcoin", "category": "coins", "trending_score": 100.0},
            {"tag": "ethereum", "category": "coins", "trending_score": 95.0},
            # DeFi
            {"tag": "defi", "category": "defi", "trending_score": 88.0},
            {"tag": "yield", "category": "defi", "trending_score": 75.0},
            {"tag": "liquidity", "category": "defi", "trending_score": 70.0},
            {"tag": "farming", "category": "defi", "trending_score": 65.0},
            # NFTs
            {"tag": "nft", "category": "nft", "trending_score": 85.0},
            {"tag": "opensea", "category": "nft", "trending_score": 70.0},
            {"tag": "metaverse", "category": "nft", "trending_score": 80.0},
            {"tag": "pfp", "category": "nft", "trending_score": 60.0},
            # Gaming
            {"tag": "gamefi", "category": "gaming", "trending_score": 75.0},
            {"tag": "p2e", "category": "gaming", "trending_score": 70.0},
            {"tag": "playtoearn", "category": "gaming", "trending_score": 68.0},
            # Platform Specific
            {"tag": "tokenlaunch", "category": "platform", "trending_score": 60.0},
            {"tag": "ailaunchpad", "category": "platform", "trending_score": 55.0},
            {"tag": "newtoken", "category": "platform", "trending_score": 50.0},
        ]

        for hashtag_data in hashtags_data:
            hashtag_data["is_trending"] = hashtag_data["trending_score"] > 60
            hashtag, created = SocialMediaHashtag.objects.get_or_create(
                tag=hashtag_data["tag"], defaults=hashtag_data
            )
            if created:
                self.stdout.write(f"  ✓ Created hashtag: #{hashtag.tag}")
            else:
                self.stdout.write(f"  - Hashtag already exists: #{hashtag.tag}")

    def create_achievements(self):
        """Create default achievements"""
        self.stdout.write("Creating Default Achievements...")

        achievements_data = [
            # Onboarding
            {
                "name": "Welcome Aboard",
                "description": "Completed account setup and profile",
                "icon": "👋",
                "category": "onboarding",
                "points": 100,
                "requirements": {"action": "profile_complete"},
                "is_active": True,
            },
            {
                "name": "First Steps",
                "description": "Created your first token launch project",
                "icon": "🚀",
                "category": "launches",
                "points": 250,
                "requirements": {"action": "first_launch_created"},
                "is_active": True,
            },
            # Social Media
            {
                "name": "Social Butterfly",
                "description": "Connected your first social media account",
                "icon": "🦋",
                "category": "social",
                "points": 150,
                "requirements": {"action": "social_account_connected"},
                "is_active": True,
            },
            {
                "name": "Content Creator",
                "description": "Published 10 social media posts",
                "icon": "📝",
                "category": "social",
                "points": 500,
                "requirements": {"action": "posts_published", "count": 10},
                "is_active": True,
            },
            # AI Interaction
            {
                "name": "AI Enthusiast",
                "description": "Had your first conversation with an AI agent",
                "icon": "🤖",
                "category": "ai",
                "points": 200,
                "requirements": {"action": "first_ai_interaction"},
                "is_active": True,
            },
            {
                "name": "AI Power User",
                "description": "Used AI agents 50 times",
                "icon": "⚡",
                "category": "ai",
                "points": 1000,
                "requirements": {"action": "ai_interactions", "count": 50},
                "is_active": True,
            },
            # Community
            {
                "name": "Helper",
                "description": "Helped 5 community members",
                "icon": "🤝",
                "category": "community",
                "points": 300,
                "requirements": {"action": "community_help", "count": 5},
                "is_active": True,
            },
            {
                "name": "Veteran",
                "description": "Active for 30 consecutive days",
                "icon": "🏆",
                "category": "engagement",
                "points": 750,
                "requirements": {"action": "daily_streak", "count": 30},
                "is_active": True,
            },
            # Launch Success
            {
                "name": "Successful Launch",
                "description": "Successfully launched a token",
                "icon": "🎯",
                "category": "launches",
                "points": 1500,
                "requirements": {"action": "successful_launch"},
                "is_active": True,
            },
            {
                "name": "Serial Launcher",
                "description": "Launched 5 successful projects",
                "icon": "🏅",
                "category": "launches",
                "points": 5000,
                "requirements": {"action": "successful_launches", "count": 5},
                "is_active": True,
            },
        ]

        for achievement_data in achievements_data:
            achievement, created = Achievement.objects.get_or_create(
                name=achievement_data["name"], defaults=achievement_data
            )
            if created:
                self.stdout.write(f"  ✓ Created achievement: {achievement.name}")
            else:
                self.stdout.write(f"  - Achievement already exists: {achievement.name}")

    def create_superuser(self, username, email):
        """Create superuser account"""
        self.stdout.write("Creating Superuser Account...")

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"  - Superuser {username} already exists")
            return

        # Create superuser
        superuser = User.objects.create_superuser(
            username=username,
            email=email,
            password="admin123",  # Default password - should be changed
            first_name="AI LaunchPad",
            last_name="Admin",
        )

        # Set additional user properties
        superuser.level = 10
        superuser.xp = 10000
        superuser.save()

        self.stdout.write(self.style.SUCCESS(f"  ✓ Created superuser: {username}"))
        self.stdout.write(
            self.style.WARNING(f"  ⚠️  Default password: admin123 (CHANGE THIS!)")
        )
