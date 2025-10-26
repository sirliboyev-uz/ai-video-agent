"""Video assembly agent using FFmpeg."""
import tempfile
from typing import Dict, Any, List
from pathlib import Path

from src.utils.ffmpeg_utils import FFmpegUtils
from src.utils.storage import StorageHandler


class AssemblyAgent:
    """Agent for assembling final video using FFmpeg."""

    def __init__(self):
        """Initialize assembly agent."""
        self.ffmpeg = FFmpegUtils()
        self.storage = StorageHandler()

    async def assemble_video(
        self,
        image_paths: List[str],
        audio_path: str,
        video_id: str,
        duration: int = 60,
        resolution: str = "1080x1920"
    ) -> Dict[str, Any]:
        """
        Assemble final video from images and audio.

        Args:
            image_paths: List of image file paths
            audio_path: Audio file path
            video_id: Video UUID
            duration: Target duration in seconds
            resolution: Video resolution

        Returns:
            Video data with path and metadata
        """
        print(f"🎬 Assembling video from {len(image_paths)} images")

        # Check FFmpeg installation
        if not self.ffmpeg.check_ffmpeg_installed():
            raise RuntimeError(
                "FFmpeg is not installed. Install with: brew install ffmpeg"
            )

        # Create temporary output file
        temp_output = tempfile.mktemp(suffix='.mp4')

        try:
            # Assemble video
            print(f"   🔧 Running FFmpeg...")
            result = await self.ffmpeg.create_video_from_images_and_audio(
                image_paths=image_paths,
                audio_path=audio_path,
                output_path=temp_output,
                duration=duration,
                fps=30,
                resolution=resolution
            )

            # Save to final location
            print(f"   💾 Saving final video...")
            final_path = await self.storage.save_video(
                video_path=temp_output,
                video_id=video_id
            )

            metadata = result["metadata"]

            print(f"   ✅ Video assembled successfully")
            print(f"   📊 Duration: {metadata.get('duration', 0):.1f}s")
            print(f"   📁 Size: {metadata.get('size_mb', 0):.2f} MB")
            print(f"   📐 Resolution: {metadata.get('width', 0)}x{metadata.get('height', 0)}")
            print(f"   🎞️  Saved to: {final_path}")

            return {
                "video_path": final_path,
                "metadata": metadata,
                "cost_usd": 0.0  # FFmpeg is free!
            }

        except Exception as e:
            # Clean up temp file if it exists
            if Path(temp_output).exists():
                Path(temp_output).unlink()
            raise Exception(f"Video assembly failed: {str(e)}")

    async def assemble_video_from_clips(
        self,
        video_clip_paths: List[str],
        audio_path: str,
        video_id: str,
        resolution: str = "1080x1920"
    ) -> Dict[str, Any]:
        """
        Assemble final video from Sora 2 video clips and audio.

        Args:
            video_clip_paths: List of Sora 2 video clip paths
            audio_path: Audio file path (voiceover)
            video_id: Video UUID
            resolution: Target resolution (default: 1080x1920 for 9:16)

        Returns:
            Video data with path and metadata
        """
        print(f"🎬 Assembling video from {len(video_clip_paths)} Sora 2 clips")

        # Check FFmpeg installation
        if not self.ffmpeg.check_ffmpeg_installed():
            raise RuntimeError(
                "FFmpeg is not installed. Install with: brew install ffmpeg"
            )

        # Create temporary output file
        temp_output = tempfile.mktemp(suffix='.mp4')

        try:
            # Concatenate video clips with audio overlay
            print(f"   🔧 Concatenating {len(video_clip_paths)} video clips...")
            result = await self.ffmpeg.concatenate_videos(
                video_paths=video_clip_paths,
                audio_path=audio_path,
                output_path=temp_output,
                resolution=resolution
            )

            # Save to final location
            print(f"   💾 Saving final video...")
            final_path = await self.storage.save_video(
                video_path=temp_output,
                video_id=video_id
            )

            metadata = result["metadata"]

            print(f"   ✅ Video assembled successfully")
            print(f"   📊 Duration: {metadata.get('duration', 0):.1f}s")
            print(f"   📁 Size: {metadata.get('size_mb', 0):.2f} MB")
            print(f"   📐 Resolution: {metadata.get('width', 0)}x{metadata.get('height', 0)}")
            print(f"   🎞️  Clips concatenated: {result.get('num_clips', 0)}")
            print(f"   🎞️  Saved to: {final_path}")

            return {
                "video_path": final_path,
                "metadata": metadata,
                "num_clips": result.get('num_clips', 0),
                "cost_usd": 0.0  # FFmpeg is free!
            }

        except Exception as e:
            # Clean up temp file if it exists
            if Path(temp_output).exists():
                Path(temp_output).unlink()
            raise Exception(f"Video assembly from clips failed: {str(e)}")
