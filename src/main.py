"""FastAPI application entry point for AI Video Agent."""
from datetime import datetime
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src.config import settings
from src.models import init_db


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )
