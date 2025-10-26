"""Storage handler for video assets (local/MinIO)."""
import uuid
from pathlib import Path
from typing import Optional
import aiofiles

from src.config import settings


class StorageHandler:
    """Handle file storage operations (local for MVP, MinIO-ready)."""

    def __init__(self):
        """Initialize storage handler."""
        self.provider = settings.STORAGE_PROVIDER
        self.local_path = Path(settings.LOCAL_STORAGE_PATH).resolve()  # Use absolute path

        # Create local storage directories
        if self.provider == "local":
            self.local_path.mkdir(parents=True, exist_ok=True)
            (self.local_path / "videos").mkdir(exist_ok=True)
            (self.local_path / "audio").mkdir(exist_ok=True)
            (self.local_path / "images").mkdir(exist_ok=True)

    async def save_audio(self, audio_bytes: bytes, video_id: str) -> str:
        """
        Save audio file.

        Args:
            audio_bytes: Audio data
            video_id: Video UUID

        Returns:
            File path or URL
        """
        if self.provider == "local":
            file_path = self.local_path / "audio" / f"{video_id}.mp3"

            async with aiofiles.open(file_path, "wb") as f:
                await f.write(audio_bytes)

            return str(file_path)

        elif self.provider == "minio":
            # MinIO implementation (Phase 3)
            raise NotImplementedError("MinIO support coming in Phase 3")

        else:
            raise ValueError(f"Unsupported storage provider: {self.provider}")

    async def save_image(self, image_bytes: bytes, video_id: str, scene_number: int) -> str:
        """
        Save image file.

        Args:
            image_bytes: Image data
            video_id: Video UUID
            scene_number: Scene index

        Returns:
            File path or URL
        """
        if self.provider == "local":
            # Create video-specific directory
            video_dir = self.local_path / "images" / video_id
            video_dir.mkdir(parents=True, exist_ok=True)

            file_path = video_dir / f"scene_{scene_number}.png"

            async with aiofiles.open(file_path, "wb") as f:
                await f.write(image_bytes)

            return str(file_path)

        elif self.provider == "minio":
            raise NotImplementedError("MinIO support coming in Phase 3")

        else:
            raise ValueError(f"Unsupported storage provider: {self.provider}")

    async def save_video(self, video_path: str, video_id: str) -> str:
        """
        Save final video file.

        Args:
            video_path: Temporary video file path
            video_id: Video UUID

        Returns:
            Final file path or URL
        """
        if self.provider == "local":
            dest_path = self.local_path / "videos" / f"{video_id}.mp4"

            # Move file from temp location
            import shutil
            shutil.move(video_path, dest_path)

            return str(dest_path)

        elif self.provider == "minio":
            raise NotImplementedError("MinIO support coming in Phase 3")

        else:
            raise ValueError(f"Unsupported storage provider: {self.provider}")

    async def download_image(self, url: str) -> bytes:
        """
        Download image from URL.

        Args:
            url: Image URL

        Returns:
            Image bytes
        """
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content

    async def get_file(self, file_path: str) -> bytes:
        """
        Read file from storage.

        Args:
            file_path: File path

        Returns:
            File contents
        """
        if self.provider == "local":
            async with aiofiles.open(file_path, "rb") as f:
                return await f.read()

        elif self.provider == "minio":
            raise NotImplementedError("MinIO support coming in Phase 3")

        else:
            raise ValueError(f"Unsupported storage provider: {self.provider}")

    def get_url(self, file_path: str) -> str:
        """
        Get public URL for file.

        Args:
            file_path: File path

        Returns:
            Public URL (for local, returns file path)
        """
        if self.provider == "local":
            # For MVP, return local file path
            # In production with MinIO, return presigned URL
            return file_path

        elif self.provider == "minio":
            raise NotImplementedError("MinIO support coming in Phase 3")

        else:
            raise ValueError(f"Unsupported storage provider: {self.provider}")
