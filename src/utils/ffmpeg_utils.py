"""FFmpeg utilities for video assembly."""
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional
import json


class FFmpegUtils:
    """FFmpeg wrapper for video composition."""

    @staticmethod
    async def create_video_from_images_and_audio(
        image_paths: List[str],
        audio_path: str,
        output_path: str,
        duration: int = 60,
        fps: int = 30,
        resolution: str = "1080x1920"  # 9:16 vertical
    ) -> dict:
        """
        Create video from images and audio using FFmpeg.

        Args:
            image_paths: List of image file paths
            audio_path: Audio file path
            output_path: Output video path
            duration: Total video duration in seconds
            fps: Frames per second
            resolution: Video resolution (width x height)

        Returns:
            Video metadata
        """
        if not image_paths:
            raise ValueError("At least one image is required")

        # Calculate duration per image
        num_images = len(image_paths)
        duration_per_image = duration / num_images

        # Create temp file list for FFmpeg concat
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            concat_file = f.name
            for img_path in image_paths:
                # FFmpeg concat format
                f.write(f"file '{img_path}'\n")
                f.write(f"duration {duration_per_image}\n")
            # Repeat last image to avoid FFmpeg concat issues
            f.write(f"file '{image_paths[-1]}'\n")

        try:
            # FFmpeg command for video creation
            # 1. Create video from images with crossfade transitions
            # 2. Add audio
            # 3. Encode with H.264
            width, height = resolution.split('x')

            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-i', audio_path,
                '-vsync', 'vfr',
                '-pix_fmt', 'yuv420p',
                '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1',
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-shortest',  # Match shortest stream (audio or video)
                '-movflags', '+faststart',  # Enable fast start for web playback
                '-y',  # Overwrite output file
                output_path
            ]

            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Get video metadata
            metadata = FFmpegUtils.get_video_metadata(output_path)

            return {
                "success": True,
                "output_path": output_path,
                "metadata": metadata
            }

        except subprocess.CalledProcessError as e:
            raise Exception(f"FFmpeg error: {e.stderr}")

        finally:
            # Clean up temp file
            Path(concat_file).unlink(missing_ok=True)

    @staticmethod
    def get_video_metadata(video_path: str) -> dict:
        """
        Get video metadata using ffprobe.

        Args:
            video_path: Path to video file

        Returns:
            Video metadata
        """
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            # Extract relevant metadata
            format_info = data.get('format', {})
            video_stream = next(
                (s for s in data.get('streams', []) if s['codec_type'] == 'video'),
                {}
            )

            return {
                "duration": float(format_info.get('duration', 0)),
                "size_bytes": int(format_info.get('size', 0)),
                "size_mb": round(int(format_info.get('size', 0)) / (1024 * 1024), 2),
                "bit_rate": int(format_info.get('bit_rate', 0)),
                "width": int(video_stream.get('width', 0)),
                "height": int(video_stream.get('height', 0)),
                "fps": eval(video_stream.get('r_frame_rate', '30/1'))  # Convert fraction to float
            }

        except Exception as e:
            return {
                "error": f"Failed to get metadata: {str(e)}"
            }

    @staticmethod
    async def add_captions(
        video_path: str,
        output_path: str,
        subtitle_text: str,
        font_size: int = 24,
        font_color: str = "white"
    ) -> str:
        """
        Add burned-in captions to video.

        Args:
            video_path: Input video path
            output_path: Output video path
            subtitle_text: Caption text
            font_size: Font size
            font_color: Font color

        Returns:
            Output video path
        """
        # Create SRT subtitle file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False) as f:
            srt_file = f.name
            # Simple SRT format
            f.write("1\n")
            f.write("00:00:00,000 --> 00:01:00,000\n")
            f.write(f"{subtitle_text}\n\n")

        try:
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', f"subtitles={srt_file}:force_style='FontSize={font_size},PrimaryColour=&H{font_color}&'",
                '-c:a', 'copy',
                '-y',
                output_path
            ]

            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return output_path

        except subprocess.CalledProcessError as e:
            raise Exception(f"Caption adding failed: {e.stderr}")

        finally:
            Path(srt_file).unlink(missing_ok=True)

    @staticmethod
    async def concatenate_videos(
        video_paths: List[str],
        audio_path: str,
        output_path: str,
        resolution: Optional[str] = None
    ) -> dict:
        """
        Concatenate multiple video clips with audio overlay.

        Args:
            video_paths: List of video clip paths to concatenate
            audio_path: Audio file path to use as background audio
            output_path: Output video path
            resolution: Optional resolution override (e.g., "1080x1920")

        Returns:
            Video metadata
        """
        if not video_paths:
            raise ValueError("At least one video clip is required")

        # Create temp file list for FFmpeg concat
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            concat_file = f.name
            for video_path in video_paths:
                # FFmpeg concat format for video files
                f.write(f"file '{video_path}'\n")

        try:
            # Build FFmpeg command
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,  # Video clips
                '-i', audio_path,   # Background audio
                '-map', '0:v',      # Use video from concat
                '-map', '1:a',      # Use audio from audio file
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-shortest',  # Match shortest stream
                '-movflags', '+faststart',
                '-y',
                output_path
            ]

            # Add resolution scaling if specified
            if resolution:
                width, height = resolution.split('x')
                cmd.insert(-3, '-vf')
                cmd.insert(-3, f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1')

            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Get video metadata
            metadata = FFmpegUtils.get_video_metadata(output_path)

            return {
                "success": True,
                "output_path": output_path,
                "metadata": metadata,
                "num_clips": len(video_paths)
            }

        except subprocess.CalledProcessError as e:
            raise Exception(f"FFmpeg concatenation error: {e.stderr}")

        finally:
            # Clean up temp file
            Path(concat_file).unlink(missing_ok=True)

    @staticmethod
    def check_ffmpeg_installed() -> bool:
        """Check if FFmpeg is installed."""
        try:
            subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
