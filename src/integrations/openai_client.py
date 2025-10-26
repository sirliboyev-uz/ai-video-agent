"""OpenAI API client for GPT-4o and DALL-E 3."""
import base64
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI

from src.config import settings


class OpenAIClient:
    """Async OpenAI client wrapper."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_gpt = "gpt-4o"  # Latest GPT-4o model
        self.model_dalle = "dall-e-3"

    async def generate_script(
        self,
        topic: str,
        style: str,
        duration: int,
        brand_voice: str,
        niche: str,
        include_timestamps: bool = False
    ) -> Dict[str, Any]:
        """
        Generate video script using GPT-4o.

        Args:
            topic: Video topic
            style: Script style (educational, entertaining, inspirational)
            duration: Target duration in seconds
            brand_voice: Brand voice guidelines
            niche: Content niche (finance, wealth, productivity)
            include_timestamps: Include precise timestamps for video-audio sync

        Returns:
            Script data with structure and metadata
        """
        timestamp_instructions = ""
        if include_timestamps:
            timestamp_instructions = """
TIMESTAMP REQUIREMENTS (CRITICAL FOR VIDEO SYNC):
- Break script into precise segments with start/end times
- Each segment should be 8-12 seconds (optimal for Sora 2 video clips)
- Include exact word count per segment for voiceover timing
- Provide visual action description matching the narration
- Format: {{"start": 0, "end": 10, "text": "...", "visual": "...", "word_count": N}}
"""

        system_prompt = f"""You are an expert YouTube Shorts scriptwriter specializing in {niche} content.
Create engaging, viral-worthy scripts optimized for {duration}-second vertical videos.

Style: {style}
Brand Voice: {brand_voice}

CRITICAL REQUIREMENTS:
1. Hook (first 3 seconds): Attention-grabbing question or statement
2. Value Proposition (3-10s): Why should they keep watching?
3. Main Content (10-{duration-10}s): Core message with actionable insights
4. Call-to-Action ({duration-10}-{duration}s): Subscribe/follow/engage
{timestamp_instructions}

Format your response as JSON:
{{
  "hook": "First 3 seconds script",
  "value_prop": "Why keep watching (3-10s)",
  "main_content": "Core content points",
  "cta": "Call to action",
  "full_script": "Complete script with timing markers",
  "estimated_word_count": number,
  "scene_descriptions": ["scene 1", "scene 2", ...],
  "segments": [{{"start": 0, "end": 10, "text": "...", "visual": "...", "word_count": N}}] (only if timestamps enabled)
}}"""

        user_prompt = f"""Create a {duration}-second {style} YouTube Short script about: {topic}

Target audience: {niche.capitalize()} enthusiasts
Platform: YouTube Shorts, TikTok, Instagram Reels
Goal: Maximum engagement and retention"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model_gpt,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,  # Creative but controlled
                max_tokens=1500,
                response_format={"type": "json_object"}
            )

            import json
            script_data = json.loads(response.choices[0].message.content)

            # Add metadata
            script_data["_meta"] = {
                "model": self.model_gpt,
                "tokens_used": {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "cost_usd": self._calculate_cost(response.usage.total_tokens, "gpt-4o")
            }

            return script_data

        except Exception as e:
            raise Exception(f"Script generation failed: {str(e)}")

    async def generate_scene_descriptions(
        self,
        script: str,
        num_scenes: int = 6
    ) -> List[str]:
        """
        Generate visual scene descriptions from script.

        Args:
            script: Full video script
            num_scenes: Number of scenes to generate

        Returns:
            List of DALL-E 3 compatible scene descriptions
        """
        prompt = f"""Analyze this video script and create {num_scenes} visual scene descriptions for DALL-E 3.

Script:
{script}

Each scene should be:
- Visually striking and professional
- Optimized for 9:16 vertical format
- Cinematic with clear focal points
- Appropriate for finance/wealth content
- High-quality photography style

Return as JSON array:
["Scene 1 description", "Scene 2 description", ...]"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model_gpt,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            return result.get("scenes", [])

        except Exception as e:
            raise Exception(f"Scene description generation failed: {str(e)}")

    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1792"  # 9:16 vertical format
    ) -> Dict[str, Any]:
        """
        Generate image using DALL-E 3.

        Args:
            prompt: Image generation prompt
            size: Image size (1024x1792 for vertical)

        Returns:
            Image data with URL and metadata
        """
        try:
            response = await self.client.images.generate(
                model=self.model_dalle,
                prompt=f"{prompt}. Professional photography, cinematic, high quality, 9:16 vertical format.",
                size=size,
                quality="hd",
                n=1
            )

            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt

            return {
                "url": image_url,
                "revised_prompt": revised_prompt,
                "size": size,
                "cost_usd": 0.04  # DALL-E 3 HD pricing
            }

        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")

    async def generate_images_batch(
        self,
        prompts: List[str],
        size: str = "1024x1792"
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple images in parallel.

        Args:
            prompts: List of image prompts
            size: Image size

        Returns:
            List of image data
        """
        import asyncio

        tasks = [self.generate_image(prompt, size) for prompt in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        images = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Warning: Image {i+1} generation failed: {result}")
                continue
            images.append(result)

        return images

    async def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 1500,
        temperature: float = 0.7,
        response_format: str = "text"
    ) -> str:
        """
        Generate text completion using GPT-4o.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0.0-1.0)
            response_format: "text" or "json_object"

        Returns:
            Generated text response
        """
        try:
            response_format_param = {"type": response_format} if response_format == "json_object" else None

            response = await self.client.chat.completions.create(
                model=self.model_gpt,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format_param
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Completion generation failed: {str(e)}")

    def _calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate API cost based on token usage."""
        # GPT-4o pricing (as of 2024)
        if model == "gpt-4o":
            # $5 per 1M input tokens, $15 per 1M output tokens
            # Simplified: average $10 per 1M tokens
            return (tokens / 1_000_000) * 10.0
        return 0.0
