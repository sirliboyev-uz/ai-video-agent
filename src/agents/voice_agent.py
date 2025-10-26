"""Voice synthesis agent using ElevenLabs."""
from typing import Dict, Any
from src.integrations.elevenlabs_client import ElevenLabsClient
from src.utils.storage import StorageHandler


class VoiceAgent:
    """Agent for voice synthesis using ElevenLabs."""

    def __init__(self):
        """Initialize voice agent."""
        self.client = ElevenLabsClient()
        self.storage = StorageHandler()

    async def synthesize_voiceover(
        self,
        script: str,
        video_id: str,
        voice_id: str = None,
        stability: float = 0.6,
        similarity_boost: float = 0.75
    ) -> Dict[str, Any]:
        """
        Generate voiceover from script.

        Args:
            script: Full script text
            video_id: Video UUID for file naming
            voice_id: Optional voice ID
            stability: Voice stability
            similarity_boost: Voice similarity

        Returns:
            Voiceover data with file path and metadata
        """
        print(f"🎤 Generating voiceover ({len(script)} characters)")

        # Synthesize speech
        voice_data = await self.client.synthesize_speech(
            text=script,
            voice_id=voice_id,
            stability=stability,
            similarity_boost=similarity_boost
        )

        # Save audio file
        audio_path = await self.storage.save_audio(
            audio_bytes=voice_data["audio_bytes"],
            video_id=video_id
        )

        print(f"   ✅ Voiceover generated and saved")
        print(f"   💰 Cost: ${voice_data['cost_usd']:.4f}")
        print(f"   📁 Saved to: {audio_path}")

        return {
            "audio_path": audio_path,
            "character_count": voice_data["character_count"],
            "cost_usd": voice_data["cost_usd"],
            "voice_id": voice_data["voice_id"],
            "settings": voice_data["settings"]
        }
