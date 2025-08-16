# AI LaunchPad - Intelligent Token Launch Platform

A modern, professional frontend application for an AI-powered token launchpad platform built with Next.js 15, TypeScript, and Tailwind CSS.

## Features

### 🤖 AI-Powered Launch System
- **Marketing Agent**: Automated marketing campaigns and trend analysis
- **Community Agent**: 24/7 community engagement and moderation
- **Analytics Agent**: Real-time performance tracking and predictive analysis  
- **Launch Agent**: Optimized deployment timing and coordination

### 🎨 Modern Design
- Clean, professional gold and white color scheme
- Smooth animations and transitions using Framer Motion
- Responsive design optimized for all devices
- Professional shadows and hover effects
- No gradients or emojis for a sophisticated look

### 🔗 Blockchain Integration
- Core blockchain integration with ethers.js
- Smart contract interaction for token deployment
- Wallet connection support (MetaMask, etc.)
- Real-time transaction tracking

### 📊 Analytics Dashboard
- Token performance metrics
- AI agent monitoring
- User engagement analytics
- Revenue tracking

## Tech Stack

- **Frontend**: Next.js 15, React 19, TypeScript
- **Styling**: Tailwind CSS 4, Custom animations
- **Blockchain**: ethers.js, Core blockchain
- **UI Components**: Headless UI, Lucide React icons
- **Animation**: Framer Motion
- **Charts**: Recharts
- **State Management**: TanStack Query
- **Notifications**: React Hot Toast

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- MetaMask or compatible Web3 wallet

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment variables:**
   Create a `.env.local` file:
   ```env
   NEXT_PUBLIC_CONTRACT_FACTORY_ADDRESS=0x...
   NEXT_PUBLIC_CONTRACT_FEE_MANAGER_ADDRESS=0x...
   NEXT_PUBLIC_CORE_RPC_URL=https://rpc.coredao.org
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── app/
│   ├── dashboard/          # Dashboard pages
│   ├── globals.css         # Global styles
│   ├── layout.tsx          # Root layout
│   ├── page.tsx           # Home page
│   └── providers.tsx      # App providers
├── components/
│   ├── Features.tsx       # Features section
│   ├── Hero.tsx          # Hero section
│   ├── LaunchPad.tsx     # Token launch form
│   ├── Navigation.tsx    # Navigation bar
│   └── Stats.tsx         # Statistics section
├── lib/
│   ├── constants.ts      # App constants
│   └── contracts.ts      # Smart contract utilities
└── types/
    └── global.d.ts       # Global type definitions
```

## Smart Contract Integration

The application integrates with these smart contracts:

### TokenFactory Contract
- `createToken()` - Deploy new tokens with AI agents
- `getLaunch()` - Retrieve launch information
- `getUserLaunches()` - Get user's token launches
- `isAgentEnabled()` - Check AI agent status

### FeeManager Contract  
- `processFees()` - Handle platform and AI service fees
- `getFeeRecord()` - Retrieve fee payment records

## AI Agent Types

The platform supports four types of AI agents:

1. **Marketing Agent (1)** - Social media automation, trend analysis
2. **Community Agent (2)** - Discord/Telegram moderation, user support  
3. **Analytics Agent (4)** - Performance tracking, insights generation
4. **Launch Agent (8)** - Deployment optimization, timing strategies

Agents can be combined using bitmask operations for custom configurations.

## Fee Structure

- **Platform Fee**: 0.01 CORE (base fee for token creation)
- **AI Agent Fee**: 0.005 CORE per selected agent
- **Total Fee**: Platform fee + (Agent count × Agent fee)

## Key Components

### Hero Section
- Animated introduction with floating elements
- AI agent preview cards
- Call-to-action buttons

### Features Section  
- Detailed AI agent capabilities
- Professional card layouts with hover effects
- Feature benefit lists

### Launch Pad
- Token configuration form
- AI agent selection interface
- Real-time fee calculation
- Smart contract integration

### Dashboard
- User token portfolio
- Performance analytics
- AI agent management
- Interactive charts

## Styling Guidelines

### Color Palette
- **Primary Gold**: `#f5b041` (buttons, accents)
- **Gold Variants**: 50-950 scale for different contexts
- **Neutral Grays**: Clean backgrounds and text
- **White**: Primary background color

### Animation Principles
- Subtle entrance animations (slide-up, fade-in)
- Smooth hover effects with scale transforms
- Professional shadow transitions
- Performance-optimized animations

### Typography
- Inter font family for modern readability
- Consistent font weight hierarchy
- Proper text color contrast ratios

## Development

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Code Quality
- TypeScript for type safety
- ESLint for code quality
- Prettier for code formatting
- Tailwind CSS for consistent styling

## Deployment

### Vercel (Recommended)
1. Connect your GitHub repository to Vercel
2. Configure environment variables
3. Deploy automatically on push

### Manual Deployment
1. Build the application: `npm run build`
2. Deploy the `out` folder to your hosting provider

## License

This project is licensed under the MIT License.

---

Built with ❤️ for the future of decentralized token launches.
