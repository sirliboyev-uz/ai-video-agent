# System Architecture

## Overview

AI Video Agent uses a **6-phase pipeline** architecture with async processing, background task queues, and multi-platform publishing.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Web UI)                        │
│  - Video Studio (creation interface)                           │
│  - Analytics Dashboard (performance metrics)                   │
│  - Settings (API keys, brand voice, templates)                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/WebSocket
┌─────────────────────▼───────────────────────────────────────────┐
│                     FastAPI Backend                             │
│  - REST API endpoints (/api/video/*, /api/analytics/*)         │
│  - Server-Sent Events (SSE) for real-time progress             │
│  - Authentication & authorization                               │
└─────────────────────┬───────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┬───────────────┐
        │             │             │             │               │
┌───────▼─────┐ ┌────▼────┐ ┌──────▼──────┐ ┌────▼────┐ ┌────────▼────────┐
│   Video     │ │Publishing│ │  Analytics  │ │Monetize │ │   Background    │
│   Service   │ │ Service  │ │   Service   │ │ Service │ │   Task Queue    │
│             │ │          │ │             │ │         │ │   (Celery)      │
│ Orchestrates│ │Multi-plat│ │Performance  │ │Revenue  │ │                 │
│ 6 phases    │ │upload    │ │tracking     │ │tracking │ │ - Video gen     │
└─────┬───────┘ └────┬─────┘ └──────┬──────┘ └────┬────┘ │ - Batch process │
      │              │              │             │      │ - Scheduled jobs│
      │              │              │             │      └────────┬────────┘
      │              │              │             │               │
┌─────▼──────────────▼──────────────▼─────────────▼───────────────▼─────────┐
│                           Agent Layer                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────────────────┐│
│  │Trend Agent  │ │Script Agent │ │Voice Agent  │ │Visual Agent          ││
│  │             │ │             │ │             │ │                      ││
│  │Google Trends│ │GPT-4o       │ │ElevenLabs   │ │DALL-E 3              ││
│  │YouTube API  │ │Prompt cache │ │Voice clone  │ │Scene generation      ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └──────────────────────┘│
│  ┌─────────────────────────────┐ ┌────────────────────────────────────────┐│
│  │Assembly Agent               │ │Publishing Coordinator                  ││
│  │                             │ │                                        ││
│  │FFmpeg video composition     │ │YouTube/TikTok/Instagram upload         ││
│  │Captions, transitions        │ │Metadata optimization, compliance       ││
│  └─────────────────────────────┘ └────────────────────────────────────────┘│
└───────────────────────────────┬────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼────────────────────────────────────────────┐
│                      Integration Layer                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐ │
│  │OpenAI Client │ │ElevenLabs    │ │YouTube Client│ │TikTok Client     │ │
│  │              │ │Client        │ │              │ │                  │ │
│  │GPT-4o        │ │Voice synth   │ │Data API      │ │Direct Post API   │ │
│  │DALL-E 3      │ │Voice cloning │ │Upload API    │ │Analytics API     │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                      │
│  │Google Trends │ │Pictory API   │ │MinIO Storage │                      │
│  │Client        │ │(optional)    │ │Client        │                      │
│  └──────────────┘ └──────────────┘ └──────────────┘                      │
└───────────────────────────────┬────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼────────────────────────────────────────────┐
│                         Data Layer                                         │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────┐  │
│  │PostgreSQL Database  │  │Redis Cache/Queue    │  │MinIO Storage     │  │
│  │                     │  │                     │  │                  │  │
│  │- Videos             │  │- Celery tasks       │  │- Video files     │  │
│  │- Scripts            │  │- Session cache      │  │- Audio files     │  │
│  │- Trends             │  │- Rate limiting      │  │- Image assets    │  │
│  │- Analytics          │  │                     │  │                  │  │
│  │- Users              │  │                     │  │                  │  │
│  └─────────────────────┘  └─────────────────────┘  └──────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

## 6-Phase Video Pipeline

### Phase 1: Trend Discovery
**Input**: Topic/niche (e.g., "passive income")
**Agent**: TrendAgent
**Process**:
1. Query Google Trends API for rising topics
2. Fetch YouTube trending videos in niche
3. Analyze engagement metrics (views, likes, comments)
4. Score topics by virality potential
5. Store top 10 topics in database

**Output**: Ranked list of trending topics with metadata
**Duration**: 10-15 seconds
**Cost**: $0.00 (free APIs)

### Phase 2: Script Generation
**Input**: Selected topic + brand voice template
**Agent**: ScriptAgent
**Process**:
1. Construct GPT-4o prompt with:
   - Topic context
   - Target duration (15-90s)
   - Platform (YouTube Shorts/TikTok)
   - Brand voice guidelines
   - Viral hook templates
2. Generate 60-second script structure:
   - Hook (0-3s): Attention grabber
   - Value prop (3-10s): Core message
   - Content (10-50s): Main points
   - CTA (50-60s): Action/subscribe
3. Validate script length and structure
4. Cache prompt for 90% cost reduction

**Output**: Structured script with timing markers
**Duration**: 3-5 seconds
**Cost**: $0.08 per script

### Phase 3: Voiceover Synthesis
**Input**: Script text + voice settings
**Agent**: VoiceAgent
**Process**:
1. Split script into natural speech segments
2. Configure voice parameters:
   - Voice ID (custom cloned voice)
   - Stability: 0.5-0.7 (natural variation)
   - Similarity boost: 0.75 (voice consistency)
   - Style exaggeration: 0.3 (subtle emotion)
3. Synthesize audio via ElevenLabs API
4. Validate audio duration matches target
5. Upload to MinIO storage

**Output**: MP3 audio file (48kHz, mono)
**Duration**: 5-8 seconds
**Cost**: $0.05 per 30 seconds

### Phase 4: Visual Generation
**Input**: Script + scene descriptions
**Agent**: VisualAgent
**Process**:
1. GPT-4o analyzes script → generates 6 scene descriptions
2. Parallel DALL-E 3 requests for each scene:
   - Style: "cinematic, professional, 9:16 vertical"
   - Quality: "hd"
   - Size: 1024x1792 (vertical format)
3. Download images to local storage
4. Validate image dimensions and quality

**Output**: 6 scene images (PNG, 9:16 aspect ratio)
**Duration**: 15-20 seconds (parallel processing)
**Cost**: $0.24 (6 images × $0.04)

### Phase 5: Video Assembly
**Input**: Audio + images + script timing
**Agent**: AssemblyAgent
**Process**:
1. Calculate scene durations from audio length
2. FFmpeg video composition:
   ```bash
   ffmpeg -loop 1 -t 10 -i scene1.png \
          -loop 1 -t 10 -i scene2.png \
          ... \
          -i audio.mp3 \
          -filter_complex "[0:v]scale=1080:1920,setsar=1[v0]; \
                           [1:v]scale=1080:1920,setsar=1[v1]; \
                           [v0][v1]concat=n=6:v=1:a=0[outv]" \
          -map "[outv]" -map 6:a \
          -c:v libx264 -preset fast -crf 23 \
          -c:a aac -b:a 128k \
          -movflags +faststart \
          output.mp4
   ```
3. Add auto-generated captions (FFmpeg subtitles)
4. Add transitions (crossfade between scenes)
5. Burn-in branding (watermark, logo)
6. Validate output: 9:16, <60s, H.264 codec

**Output**: MP4 video file (1080×1920, H.264)
**Duration**: 20-30 seconds
**Cost**: $0.00 (FFmpeg is free)

### Phase 6: Multi-Platform Publishing
**Input**: Video file + metadata
**Agent**: PublishingCoordinator
**Process**:
1. Generate platform-specific metadata:
   - YouTube: Title, description, tags, "Altered Content" flag
   - TikTok: Caption, hashtags, AI disclosure
   - Instagram: Caption (manual posting)
2. Upload to YouTube via Upload API:
   - Auto-categorize as Shorts (9:16 + <60s)
   - Set visibility (public/unlisted)
   - Add to playlist
3. Upload to TikTok via Direct Post API
4. Generate Instagram download link (manual posting)
5. Store upload IDs and platform URLs

**Output**: Published video URLs + metadata
**Duration**: 30-60 seconds
**Cost**: $0.00 (free API quotas)

## Data Models

### Video
```python
class Video(Base):
    id: UUID
    topic: str
    script: str
    voiceover_url: str
    scene_images: List[str]  # MinIO URLs
    video_url: str
    status: VideoStatus  # pending, processing, completed, failed

    # Platform publishing
    youtube_id: str
    tiktok_id: str
    instagram_url: str

    # Analytics
    youtube_views: int
    tiktok_views: int
    engagement_rate: float

    # Costs
    generation_cost: float
    estimated_revenue: float

    # Metadata
    duration: int  # seconds
    created_at: datetime
    published_at: datetime
```

### Trend
```python
class Trend(Base):
    id: UUID
    topic: str
    source: TrendSource  # google_trends, youtube
    virality_score: float
    search_volume: int
    competition_level: str
    discovered_at: datetime
    used_for_video: bool
```

### Analytics
```python
class VideoAnalytics(Base):
    video_id: UUID
    platform: Platform  # youtube, tiktok, instagram
    views: int
    likes: int
    comments: int
    shares: int
    watch_time: int  # seconds
    ctr: float  # click-through rate
    engagement_rate: float
    revenue: float  # estimated
    recorded_at: datetime
```

## API Endpoints

### Video Creation
```
POST   /api/video/create              # Create single video
POST   /api/video/create/stream       # SSE streaming progress
POST   /api/video/batch               # Batch create (up to 10)
GET    /api/video/{id}                # Get video details
GET    /api/video/list                # List all videos
DELETE /api/video/{id}                # Delete video
```

### Trend Discovery
```
GET    /api/trends/discover           # Fetch new trends
GET    /api/trends/list               # List stored trends
POST   /api/trends/score              # Score custom topic
```

### Publishing
```
POST   /api/publish/youtube/{video_id}   # Publish to YouTube
POST   /api/publish/tiktok/{video_id}    # Publish to TikTok
GET    /api/publish/status/{video_id}    # Check publish status
```

### Analytics
```
GET    /api/analytics/dashboard       # Overview metrics
GET    /api/analytics/video/{id}      # Video-specific analytics
GET    /api/analytics/trends          # Trending performance
POST   /api/analytics/refresh         # Refresh from platforms
```

### Configuration
```
GET    /api/config/brand-voice        # Get brand voice settings
PUT    /api/config/brand-voice        # Update brand voice
GET    /api/config/templates          # Get script templates
POST   /api/config/voice-clone        # Upload voice sample
```

## Background Tasks (Celery)

### Scheduled Tasks
- **Trend Discovery**: Every 6 hours
- **Analytics Refresh**: Every 1 hour
- **Batch Video Generation**: Daily at configured time
- **Cost Monitoring**: Every 15 minutes

### Async Tasks
- `generate_video_task(topic, settings)` - Full video pipeline
- `publish_video_task(video_id, platforms)` - Multi-platform upload
- `refresh_analytics_task(video_id)` - Fetch latest metrics
- `cleanup_old_assets_task()` - Delete unused files

## Security & Compliance

### Authentication
- JWT tokens for API access
- API key management for external services
- Rate limiting per user/IP

### AI Disclosure
- Automatic "Altered Content" flagging
- Metadata tagging for all AI-generated content
- Audit log of human review checkpoints

### Rate Limiting
- Max 3 video generations per user per day
- YouTube upload quota monitoring
- TikTok API rate limit compliance

### Data Privacy
- User API keys encrypted at rest
- Video assets auto-deleted after 30 days
- GDPR-compliant data export

## Scalability Considerations

### Horizontal Scaling
- Celery workers can scale independently
- Redis cluster for high-throughput queue
- MinIO for unlimited storage

### Cost Optimization
- Prompt caching (90% reduction on repeated context)
- Batch image generation (parallel DALL-E requests)
- FFmpeg over Pictory (save $0.03/video)
- Self-hosted vs cloud deployment

### Performance Targets
- Video generation: <90 seconds end-to-end
- API response time: <200ms
- Concurrent video processing: 10+ videos
- Daily throughput: 100+ videos

## Technology Decisions

### Why FastAPI?
- Async/await for parallel processing
- Automatic OpenAPI docs
- SSE support for real-time progress
- Pydantic validation

### Why PostgreSQL?
- JSON fields for flexible metadata
- Full-text search for scripts
- Strong consistency for analytics
- Better than MongoDB for structured data

### Why Celery + Redis?
- Proven background task queue
- Distributed processing
- Retry logic and error handling
- Better than RQ for complex workflows

### Why FFmpeg over Pictory?
- Free (save $0.03/video = $9/month at 300 videos)
- Full control over composition
- Faster processing (local vs API)
- Fallback to Pictory if complexity increases

### Why ElevenLabs over Azure/Google TTS?
- Superior voice quality (8/10 vs 6/10)
- Voice cloning for brand consistency
- Emotional variation
- Worth the $0.05 premium for monetization

## Next Steps

1. Set up development environment
2. Implement Phase 1-2 (Trends + Scripts)
3. Add Phase 3 (Voiceover)
4. Integrate Phase 4-5 (Visuals + Assembly)
5. Build Phase 6 (Publishing)
6. Create analytics dashboard
7. Deploy to production
