"""Database models for AI Video Agent."""
import uuid
from datetime import datetime
from typing import List, Optional
from enum import Enum

from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class VideoStatus(str, Enum):
    """Video processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PUBLISHED = "published"


class Platform(str, Enum):
    """Social media platforms."""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"


class TrendSource(str, Enum):
    """Trend discovery sources."""
    GOOGLE_TRENDS = "google_trends"
    YOUTUBE_TRENDING = "youtube_trending"
    MANUAL = "manual"


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    # API Keys (encrypted)
    openai_api_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    elevenlabs_api_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Preferences
    brand_voice: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_niche: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Usage tracking
    videos_generated: Mapped[int] = mapped_column(default=0)
    total_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    videos: Mapped[List["Video"]] = relationship("Video", back_populates="user")


class Video(Base):
    """Video generation and publishing."""
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)  # Nullable for system-generated

    # Input
    topic: Mapped[str] = mapped_column(String(500))
    niche: Mapped[str] = mapped_column(String(100))
    target_duration: Mapped[int] = mapped_column(Integer)  # seconds

    # Generated Content
    script: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    script_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # hook, cta, timing

    # Media Assets
    voiceover_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    scene_images: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # List of S3 URLs
    video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Processing
    status: Mapped[VideoStatus] = mapped_column(SQLEnum(VideoStatus), default=VideoStatus.PENDING)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processing_steps: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Phase completion tracking

    # Publishing
    youtube_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    youtube_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tiktok_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tiktok_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    instagram_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Metadata
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    ai_disclosure_added: Mapped[bool] = mapped_column(default=True)

    # Video Properties
    actual_duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # seconds
    resolution: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 1080x1920
    file_size_mb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Analytics Summary (detailed in VideoAnalytics table)
    total_views: Mapped[int] = mapped_column(default=0)
    total_likes: Mapped[int] = mapped_column(default=0)
    total_comments: Mapped[int] = mapped_column(default=0)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)

    # Costs
    generation_cost: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_revenue: Mapped[float] = mapped_column(Float, default=0.0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="videos")
    analytics: Mapped[List["VideoAnalytics"]] = relationship("VideoAnalytics", back_populates="video", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "topic": self.topic,
            "niche": self.niche,
            "status": self.status.value,
            "script": self.script,
            "video_url": self.video_url,
            "youtube_url": self.youtube_url,
            "tiktok_url": self.tiktok_url,
            "title": self.title,
            "description": self.description,
            "total_views": self.total_views,
            "engagement_rate": self.engagement_rate,
            "generation_cost": self.generation_cost,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None
        }


class Trend(Base):
    """Trending topics for video ideas."""
    __tablename__ = "trends"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    topic: Mapped[str] = mapped_column(String(500), index=True)
    niche: Mapped[str] = mapped_column(String(100), index=True)
    source: Mapped[TrendSource] = mapped_column(SQLEnum(TrendSource))

    # Scoring
    virality_score: Mapped[float] = mapped_column(Float)  # 0-100
    search_volume: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    competition_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # low, medium, high

    # Metadata
    source_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Raw data from API
    keywords: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Usage
    used_for_video: Mapped[bool] = mapped_column(default=False)
    video_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # Trend expiration

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "topic": self.topic,
            "niche": self.niche,
            "source": self.source.value,
            "virality_score": self.virality_score,
            "search_volume": self.search_volume,
            "used_for_video": self.used_for_video,
            "discovered_at": self.discovered_at.isoformat()
        }


class VideoAnalytics(Base):
    """Platform-specific video analytics."""
    __tablename__ = "video_analytics"

    id: Mapped[int] = mapped_column(primary_key=True)
    video_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("videos.id"), index=True)
    platform: Mapped[Platform] = mapped_column(SQLEnum(Platform))

    # Engagement Metrics
    views: Mapped[int] = mapped_column(default=0)
    likes: Mapped[int] = mapped_column(default=0)
    dislikes: Mapped[int] = mapped_column(default=0)
    comments: Mapped[int] = mapped_column(default=0)
    shares: Mapped[int] = mapped_column(default=0)
    saves: Mapped[int] = mapped_column(default=0)

    # Performance Metrics
    watch_time_seconds: Mapped[int] = mapped_column(default=0)
    average_view_duration: Mapped[float] = mapped_column(Float, default=0.0)
    ctr: Mapped[float] = mapped_column(Float, default=0.0)  # Click-through rate
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)

    # Revenue
    estimated_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    rpm: Mapped[float] = mapped_column(Float, default=0.0)  # Revenue per 1000 views

    # Demographics
    top_countries: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    age_groups: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    gender_split: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamp
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="analytics")

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "platform": self.platform.value,
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "engagement_rate": self.engagement_rate,
            "estimated_revenue": self.estimated_revenue,
            "recorded_at": self.recorded_at.isoformat()
        }


class BrandVoice(Base):
    """Brand voice templates for script generation."""
    __tablename__ = "brand_voices"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)

    # Voice Characteristics
    tone: Mapped[str] = mapped_column(String(100))  # professional, casual, inspirational
    style: Mapped[str] = mapped_column(String(100))  # educational, entertaining, persuasive

    # Script Guidelines
    hook_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cta_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    vocabulary_preferences: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # ElevenLabs Voice
    voice_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    voice_settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    is_default: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CostTracking(Base):
    """Daily cost tracking for budget monitoring."""
    __tablename__ = "cost_tracking"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    date: Mapped[datetime] = mapped_column(DateTime, index=True)

    # API Costs
    openai_cost: Mapped[float] = mapped_column(Float, default=0.0)
    elevenlabs_cost: Mapped[float] = mapped_column(Float, default=0.0)
    pictory_cost: Mapped[float] = mapped_column(Float, default=0.0)
    storage_cost: Mapped[float] = mapped_column(Float, default=0.0)

    # Usage
    videos_generated: Mapped[int] = mapped_column(default=0)
    total_tokens_used: Mapped[int] = mapped_column(default=0)
    total_voice_seconds: Mapped[int] = mapped_column(default=0)

    total_cost: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
