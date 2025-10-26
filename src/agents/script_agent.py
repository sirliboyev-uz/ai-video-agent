"""Script generation agent using GPT-4o."""
from typing import Dict, Any
from src.integrations.openai_client import OpenAIClient


class ScriptAgent:
    """Agent for generating video scripts using GPT-4o."""

    def __init__(self):
        """Initialize script agent."""
        self.client = OpenAIClient()

    async def generate_script(
        self,
        topic: str,
        style: str = "educational",
        duration: int = 60,
        niche: str = "finance",
        brand_voice: str = "Professional yet conversational"
    ) -> Dict[str, Any]:
        """
        Generate complete video script.

        Args:
            topic: Video topic
            style: Script style
            duration: Target duration in seconds
            niche: Content niche
            brand_voice: Brand voice guidelines

        Returns:
            Complete script with structure and metadata
        """
        print(f"📝 Generating script for: {topic}")
        print(f"   Style: {style} | Duration: {duration}s | Niche: {niche}")

        script_data = await self.client.generate_script(
            topic=topic,
            style=style,
            duration=duration,
            brand_voice=brand_voice,
            niche=niche
        )

        # Validate script structure
        required_keys = ["hook", "value_prop", "main_content", "cta", "full_script"]
        missing = [key for key in required_keys if key not in script_data]

        if missing:
            raise ValueError(f"Script missing required fields: {missing}")

        print(f"   ✅ Script generated ({script_data.get('estimated_word_count', 0)} words)")
        print(f"   💰 Cost: ${script_data['_meta']['cost_usd']:.4f}")

        return script_data
