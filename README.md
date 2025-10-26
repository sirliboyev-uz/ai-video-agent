# AI Video Agent - Automated Social Media Video Platform

**Semi-automated AI video creation system for YouTube Shorts, TikTok, and Instagram Reels**

Focus: Finance/wealth content optimization with 70% human creative input + 30% AI automation

## Project Overview

A production-ready platform that orchestrates the complete video creation pipeline:
- Trend discovery (Google Trends + YouTube API)
- Script generation (GPT-4o with brand voice)
- Voiceover synthesis (ElevenLabs)
- Visual generation (DALL-E 3)
- Video assembly (FFmpeg/Pictory)
- Multi-platform publishing (YouTube Shorts, TikTok)
- Analytics feedback loop

### Key Differentiators

- **Short-form only**: 15-90 second videos optimized for social media
- **Multi-platform**: YouTube Shorts, TikTok, Instagram Reels
- **Compliance-first**: AI disclosure, quality checkpoints, rate limiting
- **Analytics-driven**: Performance tracking with automated optimization
- **Monetization focus**: Ad revenue, email capture, affiliate integration

### Target Metrics

- **Cost**: $0.43-0.50 per video (300 videos/month = $150)
- **Quality**: 8/10 professional grade
- **Revenue Goal**: $2,000-10,000/month within 12-18 months
- **Volume**: 2-3 videos/day (60-90/month initially)

## Technology Stack

### Core Infrastructure
- **Framework**: FastAPI (async Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Task Queue**: Celery + Redis (for background video processing)
- **Storage**: MinIO (self-hosted S3-compatible storage)
- **Hosting**: Railway/Render/Fly.io

### AI & Media Services
- **Script Generation**: OpenAI GPT-4o ($0.08/script)
- **Voiceover**: ElevenLabs Creator tier ($0.05/30s)
- **Visuals**: DALL-E 3 API ($0.24 for 6 images)
- **Video Assembly**: FFmpeg (free) + Pictory API fallback ($0.03/video)
- **Trend Research**: Google Trends API + YouTube Data API

### Platform Integrations
- **YouTube**: Data API v3 + Upload API
- **TikTok**: Direct Post API (requires audit)
- **Instagram**: Manual posting (API limitations)
- **Analytics**: Platform-specific APIs + custom dashboard

## Project Structure

```
ai-video-agent/
├── src/
│   ├── agents/              # AI agent implementations
│   │   ├── trend_agent.py          # Google Trends + YouTube trending
│   │   ├── script_agent.py         # GPT-4o script generation
│   │   ├── voice_agent.py          # ElevenLabs voiceover
│   │   ├── visual_agent.py         # DALL-E 3 image generation
│   │   └── assembly_agent.py       # FFmpeg video assembly
│   │
│   ├── services/            # Business logic orchestration
│   │   ├── video_service.py        # Full pipeline orchestration
│   │   ├── publishing_service.py   # Multi-platform upload
│   │   ├── analytics_service.py    # Performance tracking
│   │   └── monetization_service.py # Revenue tracking
│   │
│   ├── integrations/        # External API wrappers
│   │   ├── openai_client.py        # GPT-4o + DALL-E 3
│   │   ├── elevenlabs_client.py    # Voice synthesis
│   │   ├── youtube_client.py       # YouTube Data + Upload
│   │   ├── tiktok_client.py        # TikTok Direct Post
│   │   └── google_trends.py        # Trend discovery
│   │
│   ├── models/              # Database models & schemas
│   │   ├── database.py             # SQLAlchemy models
│   │   ├── schemas.py              # Pydantic request/response
│   │   └── __init__.py
│   │
│   ├── utils/               # Helper functions
│   │   ├── validators.py           # Input validation
│   │   ├── ffmpeg_utils.py         # Video processing
│   │   ├── cost_calculator.py      # Cost estimation
│   │   └── compliance.py           # AI disclosure helpers
│   │
│   ├── templates/           # Frontend UI
│   │   ├── index.html              # Main dashboard
│   │   ├── video_studio.html       # Video creation UI
│   │   └── analytics.html          # Analytics dashboard
│   │
│   ├── config.py            # Configuration management
│   └── main.py              # FastAPI application
│
├── data/                    # Database & local storage
├── scripts/                 # Utility scripts
├── tests/                   # Test suites
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
└── README.md
```

## Development Roadmap

### Phase 1: Core Pipeline (Weeks 1-2)
- [ ] Project setup & infrastructure
- [ ] Database schema design
- [ ] OpenAI integration (GPT-4o + DALL-E 3)
- [ ] ElevenLabs voice synthesis
- [ ] FFmpeg video assembly
- [ ] Basic API endpoints

### Phase 2: Platform Integration (Weeks 3-4)
- [ ] YouTube Data API (trend discovery)
- [ ] YouTube Upload API (Shorts publishing)
- [ ] TikTok Direct Post API setup
- [ ] Google Trends integration
- [ ] Multi-platform metadata optimization

### Phase 3: Automation & Analytics (Weeks 5-6)
- [ ] Celery task queue for background processing
- [ ] Analytics dashboard
- [ ] Performance tracking system
- [ ] Automated feedback loop
- [ ] Cost monitoring & alerts

### Phase 4: Monetization & Compliance (Weeks 7-8)
- [ ] Email capture system
- [ ] Affiliate link integration
- [ ] AI disclosure automation
- [ ] Quality control checkpoints
- [ ] Rate limiting enforcement

### Phase 5: Optimization & Scaling (Weeks 9-12)
- [ ] Template optimization based on analytics
- [ ] Batch processing improvements
- [ ] Cost optimization
- [ ] Multi-channel management
- [ ] Advanced scheduling

## Getting Started

(Implementation details to be added during development)

### Prerequisites
- Python 3.9+
- PostgreSQL 14+
- Redis 7+
- FFmpeg
- API keys: OpenAI, ElevenLabs, YouTube, TikTok

### Installation
```bash
# Clone and setup
cd ai-video-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with API keys

# Initialize database
python scripts/init_db.py

# Run development server
python -m src.main
```

## Cost Structure

### Per Video (300 videos/month)
- Script generation: $0.08 (GPT-4o)
- Voiceover: $0.05 (ElevenLabs)
- Visuals: $0.24 (DALL-E 3, 6 images)
- Assembly: $0.03 (Pictory) or $0.00 (FFmpeg)
- **Total**: $0.40-0.43 per video

### Monthly Operating Costs
- API generation: $120-150 (300 videos)
- ElevenLabs subscription: $22-99
- Pictory subscription: $49-149 (optional)
- Hosting: $5-20
- Storage: $5-10
- **Total**: $200-400/month

### Revenue Projections (12-18 months)
- YouTube Shorts ads: $1,000-3,000
- TikTok Creator Rewards: $500-2,000
- Email list monetization: $500-2,000
- Affiliate commissions: $500-3,000
- **Target Total**: $2,500-10,000/month

## Compliance & Best Practices

### AI Disclosure (Mandatory)
- YouTube: "Altered Content" checkbox
- TikTok: AI-generated label
- Instagram: Automatic detection labels

### 70/30 Rule
- 70% human creative input (strategy, review, optimization)
- 30% AI efficiency (generation, assembly, scheduling)

### Rate Limiting
- Max 2-3 videos/day (avoid spam flags)
- Human review checkpoint before publishing
- Quality validation gates

## License

MIT

## Status

🚧 **In Development** - Architecture planning phase
