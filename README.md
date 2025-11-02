# 🎬 ETH Creators - AI-Powered Video Generation Platform

> Empowering the Ethereum creator economy with AI-generated content using OpenAI Sora 2

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://eth-creators.vercel.app)
[![Telegram Bot](https://img.shields.io/badge/telegram-@ethcreators__bot-blue)](https://t.me/ethcreators_bot)
[![License](https://img.shields.io/badge/license-MIT-green)]()

## 🏆 Hackathon Submission

**Built for:** [Hackathon Name]
**Category:** AI & Web3 Innovation
**Team:** [Your Team Name]

---

## 📹 Demo

🎥 **[Watch Demo Video](#)** (Add your demo link)
🌐 **[Live Platform](https://eth-creators.vercel.app)**
🤖 **[Try the Bot](https://t.me/ethcreators_bot)**

---

## 🎯 The Problem

The Ethereum ecosystem needs more high-quality educational and promotional content, but:

- 📉 **Content Creation Barrier**: High production costs ($500-2000/video)
- ⏰ **Time Intensive**: Traditional video production takes days/weeks
- 🎨 **Skill Gap**: Not everyone has video editing expertise
- 🌍 **Limited Reach**: Existing content doesn't serve global, multilingual audiences

## 💡 Our Solution

**ETH Creators** is an AI-powered platform that enables anyone to create professional-quality videos about Ethereum, DeFi, and Web3 in minutes using natural language prompts.

### Key Innovation
- **OpenAI Sora 2 Integration**: First Telegram bot leveraging Sora 2 for Web3 content
- **Instant Generation**: 2-5 minutes from prompt to video
- **Multi-language Support**: Create content in any language
- **Social Metrics Tracking**: Automated performance analytics
- **Creator Economy**: Built-in incentive system for top creators

---

## ✨ Features

### 🤖 AI Video Generation
- Generate 15-second professional videos with simple text prompts
- Powered by **OpenAI Sora 2** (latest AI video generation model)
- Smart content validation for Web3-appropriate material
- Automatic caption and hashtag generation

### 📱 Telegram Bot Interface
```
/create [your prompt]  → Generate AI video
/posted [social url]   → Track video performance
/stats                 → View your analytics
/leaderboard          → See top creators
```

### 📊 Analytics Dashboard
- Real-time creator leaderboard
- Video gallery with metrics (views, likes, shares)
- Social media performance tracking
- Global statistics

### 🌐 Supported Platforms
- ✅ TikTok
- ✅ Instagram Reels
- ✅ Twitter/X

---

## 🏗️ Technical Architecture

```
┌─────────────────┐
│  Telegram Bot   │ ←─── User sends /create prompt
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI + GPT-4│ ←─── Content validation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Sora 2 API     │ ←─── Video generation (2-5 min)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Supabase Storage│ ←─── Video hosting + DB
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  React Dashboard│ ←─── Public gallery
└─────────────────┘
```

### Backend Flow
1. **User Input** → Telegram command `/create [prompt]`
2. **Validation** → GPT-4 checks content appropriateness
3. **Generation** → Sora 2 creates video (~15 seconds)
4. **Storage** → Upload to Supabase Storage
5. **Metadata** → Generate captions, hashtags, thumbnails
6. **Delivery** → Send video to user via Telegram

### Social Tracking Flow
1. **User Posts** → `/posted [tiktok/instagram/twitter url]`
2. **Scraping** → Automated metrics collection (views, likes, comments)
3. **Updates** → Scheduled updates every 6 hours
4. **Leaderboard** → Real-time ranking updates

---

## 🛠️ Tech Stack

### AI & Generation
- **OpenAI Sora 2** - AI video generation
- **GPT-4** - Content validation & caption generation
- **Python 3.13** - Backend core

### Backend
- **FastAPI** - REST API & webhooks
- **python-telegram-bot** - Bot framework
- **Supabase** - Database & file storage
- **PostgreSQL** - Relational data
- **APScheduler** - Automated metrics updates

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library

### Infrastructure
- **Railway** - Backend hosting
- **Vercel** - Frontend hosting
- **GitHub Actions** - CI/CD (optional)

### APIs & Services
- **Telegram Bot API** - Chat interface
- **TikTok oEmbed API** - Metrics scraping
- **Supabase Storage** - CDN & file hosting

---

## 🚀 Getting Started

### Prerequisites
```bash
- Python 3.13+
- Node.js 18+
- Telegram Bot Token
- OpenAI API Key (with Sora 2 access)
- Supabase Account
```

### Installation

#### 1️⃣ Clone Repository
```bash
git clone https://github.com/[username]/eth-creators-hackathon.git
cd eth-creators-hackathon
```

#### 2️⃣ Backend Setup
```bash
cd uniswap_sora_bot_v2
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

Run backend:
```bash
python app.py
```

#### 3️⃣ Frontend Setup
```bash
cd lovable-api-hub
npm install
```

Create `.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_WALLETCONNECT_PROJECT_ID=your_project_id
```

Run frontend:
```bash
npm run dev
```

---

## 📖 Usage Examples

### Basic Video Generation
```
User: /create A person in Mexico City using EtherFi to buy tacos with crypto

Bot: 🎬 Generating your video...
     ⏳ 5 minutes remaining

[5 minutes later]

Bot: ✅ Your video is ready!
     📹 [video.mp4]
     💬 Caption: "Crypto meets tacos in CDMX! 🌮💰"
     🏷️ #EtherFi #DeFi #Web3 #Mexico
```

### Advanced Prompt (Cultural Context)
```
User: /create Create a video set in Monterrey showing a group of friends
at a "carnita asada" talking about how one of them no longer needs to
ask the bank for money because they use ether.fi Cash. Use northern
Mexican accent and show iconic Cerro de la Silla mountain.

Bot: ✅ Video generated with cultural_fusion category
     [Contextually accurate video with local references]
```

### Track Social Performance
```
User: /posted https://tiktok.com/@user/video/123456

Bot: ✅ Post registered!
     📊 Tracking metrics for Video #73
     🔄 Auto-updates every 6 hours
```

---

## 🎨 Content Categories

The platform supports multiple content types:

1. **DeFi Education** - Explaining Web3 concepts
2. **Product Features** - Showcasing protocols (Uniswap, Aave, EtherFi)
3. **Cultural Fusion** - Web3 meets local culture
4. **User Success** - Adoption stories
5. **Multi-Chain** - Cross-chain, L2 networks
6. **Tech Innovation** - Blockchain infrastructure



## 🔮 Future Roadmap

### Phase 1: Enhanced AI (Q1 2025)
- [ ] Custom voice narration (11Labs integration)
- [ ] Multi-scene video editing
- [ ] Brand logo/watermark overlay
- [ ] Background music selection

### Phase 2: Creator Monetization (Q2 2025)
- [ ] Token rewards for top creators
- [ ] NFT minting for viral videos
- [ ] Sponsored content marketplace
- [ ] Revenue sharing with creators

### Phase 3: Community & Scale (Q3 2025)
- [ ] Multi-bot support (Discord, WhatsApp)
- [ ] Collaborative video creation
- [ ] Template marketplace
- [ ] API access for developers

### Phase 4: DAO Governance (Q4 2025)
- [ ] Creator DAO formation
- [ ] Community voting on features
- [ ] Treasury management
- [ ] Protocol upgrades

---

## 🏆 Why This Wins

### Innovation
- **First-to-Market**: First Telegram bot using Sora 2 for Web3
- **Accessibility**: No technical skills needed
- **Speed**: 1000x faster than traditional production

### Impact
- **Creator Economy**: Democratizes content creation
- **Ethereum Adoption**: Makes Web3 education accessible
- **Global Reach**: Supports any language/culture

### Technical Excellence
- **Scalable Architecture**: Railway + Vercel auto-scaling
- **Production Ready**: Live platform with real users
- **Clean Code**: Modular, documented, maintainable

### Business Model
- **Sustainable**: Token economy + sponsored content
- **Viral Loop**: Creators promote their videos → bring users
- **Network Effects**: More creators = better content = more users

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Fork the repository
git checkout -b feature/amazing-feature
git commit -m 'Add amazing feature'
git push origin feature/amazing-feature
# Open a Pull Request
```

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 👥 Team

- **[Your Name]** - Full Stack Developer - [@yourgithub](https://github.com/yourgithub)

---

## 🙏 Acknowledgments

- **OpenAI** - Sora 2 API access
- **Ethereum Foundation** - Ecosystem support
- **Supabase** - Infrastructure hosting
- **Telegram** - Bot platform

---


---

<div align="center">

**Built with ❤️ for the Ethereum Community**

[⭐ Star this repo](https://github.com/[username]/eth-creators-hackathon) | [🐛 Report Bug](https://github.com/[username]/eth-creators-hackathon/issues) | [✨ Request Feature](https://github.com/[username]/eth-creators-hackathon/issues)

</div>
