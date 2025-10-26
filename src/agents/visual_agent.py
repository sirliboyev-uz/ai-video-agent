"""Visual generation agent using DALL-E 3."""
from typing import Dict, Any, List
from src.integrations.openai_client import OpenAIClient
from src.utils.storage import StorageHandler


class VisualAgent:
    """Agent for generating visuals using DALL-E 3."""

    def __init__(self):
        """Initialize visual agent."""
        self.client = OpenAIClient()
        self.storage = StorageHandler()

    async def generate_scene_images(
        self,
        script: str,
        video_id: str,
        num_scenes: int = 6
    ) -> Dict[str, Any]:
        """
        Generate scene images for video.

        Args:
            script: Full video script
            video_id: Video UUID for file naming
            num_scenes: Number of scenes to generate

        Returns:
            Image data with paths and metadata
        """
        print(f"🎨 Generating {num_scenes} scene images")

        # Step 1: Generate scene descriptions
        print(f"   📝 Creating scene descriptions...")
        scene_descriptions = await self.client.generate_scene_descriptions(
            script=script,
            num_scenes=num_scenes
        )

        if len(scene_descriptions) < num_scenes:
            print(f"   ⚠️  Only got {len(scene_descriptions)} descriptions, expected {num_scenes}")
            scene_descriptions = scene_descriptions + [scene_descriptions[-1]] * (num_scenes - len(scene_descriptions))

        # Step 2: Generate images in parallel
        print(f"   🖼️  Generating images...")
        image_results = await self.client.generate_images_batch(
            prompts=scene_descriptions[:num_scenes],
            size="1024x1792"  # 9:16 vertical
        )

        # Step 3: Download and save images
        print(f"   💾 Downloading and saving images...")
        image_paths = []
        total_cost = 0.0

        for i, image_data in enumerate(image_results):
            # Download image
            image_bytes = await self.storage.download_image(image_data["url"])

            # Save to storage
            image_path = await self.storage.save_image(
                image_bytes=image_bytes,
                video_id=video_id,
                scene_number=i + 1
            )

            image_paths.append(image_path)
            total_cost += image_data["cost_usd"]

        print(f"   ✅ Generated and saved {len(image_paths)} images")
        print(f"   💰 Cost: ${total_cost:.2f}")

        return {
            "image_paths": image_paths,
            "scene_descriptions": scene_descriptions[:num_scenes],
            "num_images": len(image_paths),
            "cost_usd": total_cost
        }
