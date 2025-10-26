"""Application configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Application
    APP_NAME: str = "AI Video Agent"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/ai_video_agent"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # OpenAI API
    OPENAI_API_KEY: str
    OPENAI_ORG_ID: Optional[str] = None
    AI_PROVIDER: str = "openai"  # openai or anthropic

    # Anthropic API (Optional)
    ANTHROPIC_API_KEY: Optional[str] = None

    # ElevenLabs
    ELEVENLABS_API_KEY: str
    ELEVENLABS_VOICE_ID: Optional[str] = None
    ELEVENLABS_MODEL: str = "eleven_turbo_v2_5"

    # YouTube API
    YOUTUBE_CLIENT_ID: Optional[str] = None
    YOUTUBE_CLIENT_SECRET: Optional[str] = None
    YOUTUBE_REFRESH_TOKEN: Optional[str] = None
    YOUTUBE_API_KEY: Optional[str] = None

    # TikTok API
    TIKTOK_CLIENT_KEY: Optional[str] = None
    TIKTOK_CLIENT_SECRET: Optional[str] = None
    TIKTOK_ACCESS_TOKEN: Optional[str] = None

    # Instagram API
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    INSTAGRAM_ACCOUNT_ID: Optional[str] = None

    # Storage (MinIO - Self-hosted S3-compatible)
    STORAGE_PROVIDER: str = "local"  # minio or local
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "ai-video-agent"
    MINIO_SECURE: bool = False  # True for HTTPS
    LOCAL_STORAGE_PATH: str = "./data/media"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Cost Limits
    MAX_DAILY_VIDEOS: int = 10
    MAX_MONTHLY_COST_USD: float = 500.0
    ALERT_EMAIL: Optional[str] = None

    # Video Settings
    DEFAULT_VIDEO_DURATION: int = 60  # seconds
    DEFAULT_ASPECT_RATIO: str = "9:16"
    DEFAULT_RESOLUTION: str = "1080x1920"
    VIDEO_CODEC: str = "libx264"
    VIDEO_CRF: int = 23  # 18-28, lower = higher quality

    # Script Generation
    DEFAULT_SCRIPT_STYLE: str = "educational"
    DEFAULT_NICHE: str = "finance"
    DEFAULT_BRAND_VOICE: str = "Professional yet conversational, focusing on actionable finance tips"

    # Platform Publishing
    AUTO_PUBLISH_YOUTUBE: bool = True
    AUTO_PUBLISH_TIKTOK: bool = False
    YOUTUBE_DEFAULT_VISIBILITY: str = "public"  # public, unlisted, private
    YOUTUBE_DEFAULT_CATEGORY: int = 27  # 27 = Education

    # Analytics
    ANALYTICS_REFRESH_INTERVAL_HOURS: int = 1
    METRICS_RETENTION_DAYS: int = 365

    # Rate Limiting
    MAX_VIDEOS_PER_DAY_PER_USER: int = 3
    MAX_API_REQUESTS_PER_MINUTE: int = 60

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"

    # Feature Flags
    ENABLE_VOICE_CLONING: bool = True
    ENABLE_PICTORY_FALLBACK: bool = False
    ENABLE_BATCH_GENERATION: bool = True
    ENABLE_ANALYTICS_DASHBOARD: bool = True
    ENABLE_EMAIL_CAPTURE: bool = True

    # Development
    MOCK_EXTERNAL_APIS: bool = False
    SKIP_VIDEO_GENERATION: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    def validate(self):
        """Validate critical settings."""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")

        if not self.ELEVENLABS_API_KEY:
            raise ValueError("ELEVENLABS_API_KEY is required")

        if self.ENVIRONMENT == "production" and self.SECRET_KEY == "your-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be changed in production")

        print(f"✅ Configuration validated: {self.ENVIRONMENT} mode")


# Global settings instance
settings = Settings()
