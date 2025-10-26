"""ElevenLabs API client for voice synthesis."""
from typing import Dict, Any, Optional, List
import httpx
import io
import wave

from src.config import settings


class ElevenLabsClient:
    """Async ElevenLabs client wrapper."""

    def __init__(self):
        """Initialize ElevenLabs client."""
        self.api_key = settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.model = settings.ELEVENLABS_MODEL

        # Default voice ID (can be customized)
        self.default_voice_id = settings.ELEVENLABS_VOICE_ID or "21m00Tcm4TlvDq8ikWAM"  # Rachel voice

    async def synthesize_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        stability: float = 0.6,
        similarity_boost: float = 0.75,
        style: float = 0.3
    ) -> Dict[str, Any]:
        """
        Synthesize speech from text using ElevenLabs.

        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use (default: Rachel)
            stability: Voice stability (0-1, lower = more variable)
            similarity_boost: Voice similarity (0-1, higher = more consistent)
            style: Style exaggeration (0-1, higher = more expressive)

        Returns:
            Audio data with metadata
        """
        voice_id = voice_id or self.default_voice_id

        url = f"{self.base_url}/text-to-speech/{voice_id}"

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "text": text,
            "model_id": self.model,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": True
            }
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

                audio_bytes = response.content

                # Estimate cost (ElevenLabs charges per character)
                char_count = len(text)
                cost_per_char = 0.0003  # Approximate pricing
                cost_usd = char_count * cost_per_char

                return {
                    "audio_bytes": audio_bytes,
                    "text": text,
                    "voice_id": voice_id,
                    "character_count": char_count,
                    "cost_usd": cost_usd,
                    "settings": {
                        "stability": stability,
                        "similarity_boost": similarity_boost,
                        "style": style
                    }
                }

        except httpx.HTTPStatusError as e:
            raise Exception(f"ElevenLabs API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Voice synthesis failed: {str(e)}")

    async def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available voices."""
        url = f"{self.base_url}/voices"

        headers = {"xi-api-key": self.api_key}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                return response.json()

        except Exception as e:
            raise Exception(f"Failed to fetch voices: {str(e)}")

    async def clone_voice(
        self,
        name: str,
        audio_files: list,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Clone a voice from audio samples.

        Args:
            name: Name for the cloned voice
            audio_files: List of audio file paths
            description: Optional voice description

        Returns:
            Voice ID and metadata
        """
        url = f"{self.base_url}/voices/add"

        headers = {"xi-api-key": self.api_key}

        # This is a placeholder - actual implementation requires multipart/form-data
        # For MVP, users will use pre-existing voices
        raise NotImplementedError("Voice cloning requires audio file upload - use web UI for now")

    async def synthesize_segments(
        self,
        segments: List[Dict[str, Any]],
        voice_id: Optional[str] = None,
        stability: float = 0.6,
        similarity_boost: float = 0.75,
        style: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Synthesize multiple text segments with timing information.

        Args:
            segments: List of segments with 'text' and optional timing info
            voice_id: Voice ID to use
            stability: Voice stability
            similarity_boost: Voice similarity
            style: Style exaggeration

        Returns:
            List of audio segments with duration metadata
        """
        results = []
        total_cost = 0.0

        for i, segment in enumerate(segments):
            try:
                audio_data = await self.synthesize_speech(
                    text=segment['text'],
                    voice_id=voice_id,
                    stability=stability,
                    similarity_boost=similarity_boost,
                    style=style
                )

                # Try to get actual audio duration using pydub (requires ffmpeg)
                try:
                    import subprocess
                    import tempfile
                    import os

                    # Save audio bytes to temp file
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                        tmp_file.write(audio_data['audio_bytes'])
                        tmp_path = tmp_file.name

                    # Get duration using ffprobe
                    cmd = [
                        'ffprobe',
                        '-v', 'quiet',
                        '-show_entries', 'format=duration',
                        '-of', 'default=noprint_wrappers=1:nokey=1',
                        tmp_path
                    ]

                    result = subprocess.run(cmd, capture_output=True, text=True)
                    duration = float(result.stdout.strip())

                    # Clean up temp file
                    os.unlink(tmp_path)

                except Exception as e:
                    # Fallback: estimate duration (average 150 words per minute = 2.5 words/sec)
                    word_count = len(segment['text'].split())
                    duration = word_count / 2.5

                segment_result = {
                    **audio_data,
                    "segment_index": i,
                    "duration_seconds": duration,
                    "planned_start": segment.get('start', None),
                    "planned_end": segment.get('end', None)
                }

                results.append(segment_result)
                total_cost += audio_data['cost_usd']

            except Exception as e:
                print(f"Warning: Segment {i} synthesis failed: {str(e)}")
                continue

        return results

    def calculate_cost(self, text: str) -> float:
        """Calculate estimated cost for text synthesis."""
        char_count = len(text)
        return char_count * 0.0003  # $0.30 per 1000 characters
