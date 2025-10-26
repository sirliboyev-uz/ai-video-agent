"""FastAPI application entry point for AI Video Agent."""
from datetime import datetime
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.config import settings
from src.models import init_db, get_db
from src.models.database import Video
from src.services import VideoService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("=" * 60)
    print("🚀 AI Video Agent - Starting Up")
    print("=" * 60)

    print("\n📊 Configuration:")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Debug Mode: {settings.DEBUG}")
    print(f"   Host: {settings.HOST}:{settings.PORT}")
    print(f"   Database: {settings.DATABASE_URL}")
    print(f"   AI Provider: {settings.AI_PROVIDER}")

    print("\n🗄️  Initializing database...")
    await init_db()
    print("   ✅ Database initialized")

    print("\n🔧 Validating configuration...")
    try:
        settings.validate()
        print("   ✅ Configuration validated")
    except Exception as e:
        print(f"   ⚠️  Configuration warning: {e}")
        print("   💡 Add OPENAI_API_KEY and ELEVENLABS_API_KEY to .env file")

    print("\n" + "=" * 60)
    print("✅ Application started successfully!")
    print(f"📡 API Documentation: http://localhost:{settings.PORT}/docs")
    print("=" * 60 + "\n")

    yield

    # Shutdown
    print("\n🛑 Application shutting down...")


app = FastAPI(
    title="AI Video Agent",
    description="Automated social media video generation platform with 95% AI automation",
    version="0.1.0-mvp",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve landing page."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Video Agent - Automated Video Generation</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                text-align: center;
            }
            h1 {
                font-size: 3.5rem;
                margin-bottom: 1rem;
                font-weight: 800;
            }
            .subtitle {
                font-size: 1.5rem;
                opacity: 0.9;
                margin-bottom: 3rem;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 2rem;
                margin: 3rem 0;
            }
            .stat {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                padding: 2rem;
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .stat-value {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
            }
            .stat-label {
                opacity: 0.8;
            }
            .links {
                margin-top: 3rem;
                display: flex;
                gap: 1rem;
                justify-content: center;
                flex-wrap: wrap;
            }
            .btn {
                padding: 1rem 2rem;
                border-radius: 10px;
                text-decoration: none;
                font-weight: 600;
                transition: all 0.3s;
                display: inline-block;
            }
            .btn-primary {
                background: white;
                color: #667eea;
            }
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            .btn-secondary {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid white;
            }
            .btn-secondary:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            .features {
                margin-top: 3rem;
                text-align: left;
                background: rgba(255, 255, 255, 0.1);
                padding: 2rem;
                border-radius: 15px;
            }
            .feature {
                margin: 1rem 0;
                font-size: 1.1rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI Video Agent</h1>
            <p class="subtitle">Automated Social Media Video Generation Platform</p>

            <div class="stats">
                <div class="stat">
                    <div class="stat-value">95%</div>
                    <div class="stat-label">Automation</div>
                </div>
                <div class="stat">
                    <div class="stat-value">$0.43</div>
                    <div class="stat-label">Cost per Video</div>
                </div>
                <div class="stat">
                    <div class="stat-value">90s</div>
                    <div class="stat-label">Generation Time</div>
                </div>
            </div>

            <div class="features">
                <div class="feature">✅ 6-Phase Pipeline: Research → Script → Voice → Visual → Assembly → Publish</div>
                <div class="feature">✅ Multi-Platform: YouTube Shorts, TikTok, Instagram Reels</div>
                <div class="feature">✅ AI-Powered: GPT-4o Scripts + DALL-E 3 Visuals + ElevenLabs Voice</div>
                <div class="feature">✅ Self-Hosted: MinIO Storage + PostgreSQL Database</div>
                <div class="feature">✅ Cost-Optimized: FFmpeg Assembly (Free)</div>
            </div>

            <div class="links">
                <a href="/docs" class="btn btn-primary">📚 API Documentation</a>
                <a href="/redoc" class="btn btn-secondary">📖 ReDoc</a>
                <a href="https://github.com/sirliboyev-uz/ai-video-agent" class="btn btn-secondary" target="_blank">
                    💻 GitHub
                </a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0-mvp",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT
    }


@app.get("/api/config/info")
async def config_info():
    """Get non-sensitive configuration information."""
    return {
        "environment": settings.ENVIRONMENT,
        "ai_provider": settings.AI_PROVIDER,
        "default_niche": settings.DEFAULT_NICHE,
        "default_style": settings.DEFAULT_SCRIPT_STYLE,
        "max_daily_videos": settings.MAX_DAILY_VIDEOS,
        "video_settings": {
            "duration": settings.DEFAULT_VIDEO_DURATION,
            "aspect_ratio": settings.DEFAULT_ASPECT_RATIO,
            "resolution": settings.DEFAULT_RESOLUTION
        }
    }


# ============================================================================
# Pydantic Models for API Requests/Responses
# ============================================================================

class VideoGenerateRequest(BaseModel):
    """Request model for video generation."""
    topic: str = Field(..., min_length=3, max_length=500, description="Video topic or subject")
    style: str = Field(default="educational", description="Script style (educational, entertaining, etc.)")
    niche: str = Field(default="finance", description="Content niche (finance, tech, health, etc.)")
    duration: int = Field(default=60, ge=15, le=180, description="Target duration in seconds")
    num_scenes: int = Field(default=6, ge=3, le=12, description="Number of scenes/images")
    brand_voice: str = Field(default="Professional yet conversational", description="Brand voice guidelines")

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "5 proven ways to save money in 2025",
                "style": "educational",
                "niche": "finance",
                "duration": 60,
                "num_scenes": 6,
                "brand_voice": "Professional yet conversational"
            }
        }


class VideoResponse(BaseModel):
    """Response model for video generation."""
    video_id: str
    video_path: str
    thumbnail_path: str
    duration: float
    cost_usd: float
    script: str
    metadata: dict

    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "123e4567-e89b-12d3-a456-426614174000",
                "video_path": "/storage/videos/123e4567-e89b-12d3-a456-426614174000.mp4",
                "thumbnail_path": "/storage/images/123e4567-e89b-12d3-a456-426614174000_scene_1.png",
                "duration": 62.5,
                "cost_usd": 0.43,
                "script": "Want to save money in 2025? Here are 5 proven strategies...",
                "metadata": {}
            }
        }


# ============================================================================
# Video Generation API Endpoints
# ============================================================================

@app.post("/api/video/generate", response_model=VideoResponse, tags=["Video Generation"])
async def generate_video(
    request: VideoGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a complete video through the 6-phase AI pipeline.

    This endpoint orchestrates:
    1. Script generation with GPT-4o
    2. Voice synthesis with ElevenLabs
    3. Visual generation with DALL-E 3
    4. Video assembly with FFmpeg
    5. Publishing (manual in MVP)
    6. Analytics (manual in MVP)

    Returns the complete video with metadata and cost breakdown.
    """
    try:
        video_service = VideoService()
        result = await video_service.generate_video(
            topic=request.topic,
            db=db,
            style=request.style,
            niche=request.niche,
            duration=request.duration,
            num_scenes=request.num_scenes,
            brand_voice=request.brand_voice
        )
        return VideoResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")


@app.post("/api/video/generate/stream", tags=["Video Generation"])
async def generate_video_stream(
    request: VideoGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate video with real-time progress updates via Server-Sent Events (SSE).

    Returns a stream of events showing progress through each pipeline phase:
    - start: Video generation begins
    - phase: Each phase (script, voice, visual, assembly) with status updates
    - complete: Final video ready
    - error: If generation fails

    Use EventSource API in frontend to consume this stream.
    """
    video_service = VideoService()
    return StreamingResponse(
        video_service.generate_video_stream(
            topic=request.topic,
            db=db,
            style=request.style,
            niche=request.niche,
            duration=request.duration,
            num_scenes=request.num_scenes,
            brand_voice=request.brand_voice
        ),
        media_type="text/event-stream"
    )


@app.get("/api/video/{video_id}", tags=["Video Management"])
async def get_video(
    video_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a video by its UUID.

    Returns complete video information including paths, metadata, and costs.
    """
    result = await db.execute(
        select(Video).where(Video.uuid == video_id)
    )
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(status_code=404, detail=f"Video {video_id} not found")

    return {
        "video_id": video.uuid,
        "topic": video.topic,
        "script": video.script,
        "video_path": video.video_path,
        "thumbnail_path": video.thumbnail_path,
        "status": video.status.value,
        "duration": video.duration,
        "cost_usd": video.cost_usd,
        "created_at": video.created_at.isoformat(),
        "metadata": video.metadata_
    }


@app.get("/api/video/list", tags=["Video Management"])
async def list_videos(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """
    List all videos with pagination.

    Query parameters:
    - skip: Number of videos to skip (default: 0)
    - limit: Maximum videos to return (default: 20, max: 100)
    """
    if limit > 100:
        limit = 100

    result = await db.execute(
        select(Video)
        .order_by(Video.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    videos = result.scalars().all()

    return {
        "total": len(videos),
        "skip": skip,
        "limit": limit,
        "videos": [
            {
                "video_id": v.uuid,
                "topic": v.topic,
                "status": v.status.value,
                "duration": v.duration,
                "cost_usd": v.cost_usd,
                "created_at": v.created_at.isoformat(),
                "video_path": v.video_path,
                "thumbnail_path": v.thumbnail_path
            }
            for v in videos
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )
