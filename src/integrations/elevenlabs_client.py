"""ElevenLabs API client for voice synthesis."""
from typing import Dict, Any, Optional
import httpx

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

    def calculate_cost(self, text: str) -> float:
        """Calculate estimated cost for text synthesis."""
        char_count = len(text)
        return char_count * 0.0003  # $0.30 per 1000 characters
