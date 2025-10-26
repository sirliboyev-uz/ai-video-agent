"""Video generation agent using Sora 2 via kie.ai."""
from typing import Dict, Any, List
from src.integrations.openai_client import OpenAIClient
from src.integrations.sora2_client import Sora2Client
from src.utils.storage import StorageHandler


class VideoAgent:
    """Agent for generating video clips using Sora 2."""

    def __init__(self):
        """Initialize video agent."""
        self.openai_client = OpenAIClient()
        self.sora_client = Sora2Client()
        self.storage = StorageHandler()

    async def generate_scene_videos(
        self,
        script: str,
        video_id: str,
        num_scenes: int = 6,
        duration: str = "10",
        aspect_ratio: str = "portrait"
    ) -> Dict[str, Any]:
        """
        Generate scene videos using Sora 2.

        Args:
            script: Full video script
            video_id: Video UUID for file naming
            num_scenes: Number of scenes to generate
            duration: "10" or "15" seconds per clip
            aspect_ratio: "portrait" (9:16) or "landscape" (16:9)

        Returns:
            Video data with paths and metadata
        """
        print(f"🎬 Generating {num_scenes} scene videos")

        # Step 1: Generate scene descriptions for Sora 2
        print(f"   📝 Creating scene descriptions...")
        scene_descriptions = await self.openai_client.generate_scene_descriptions(
            script=script,
            num_scenes=num_scenes
        )

        if len(scene_descriptions) < num_scenes:
            print(f"   ⚠️  Only got {len(scene_descriptions)} descriptions, expected {num_scenes}")
            scene_descriptions = scene_descriptions + [scene_descriptions[-1]] * (num_scenes - len(scene_descriptions))

        # Step 2: Enhance descriptions for Sora 2 video generation
        print(f"   ✨ Enhancing descriptions for video generation...")
        video_prompts = await self._enhance_for_video(scene_descriptions[:num_scenes])

        # Step 3: Generate videos with Sora 2
        print(f"   🎥 Generating Sora 2 videos (this may take 2-4 minutes per video)...")
        video_paths = []
        total_cost = 0.0
        failed_scenes = []

        for i, prompt in enumerate(video_prompts):
            try:
                print(f"      Scene {i+1}/{num_scenes}: Creating task...")

                # Create video generation task
                result = await self.sora_client.generate_video(
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    duration=duration,
                    remove_watermark=True
                )

                print(f"      Scene {i+1}/{num_scenes}: Task {result['task_id']} created, waiting for completion...")

                # Wait for completion with longer timeout (5 minutes per video)
                completed = await self.sora_client.wait_for_completion(
                    task_id=result['task_id'],
                    max_wait_seconds=300,  # 5 minutes
                    poll_interval=15  # Check every 15 seconds
                )

                # Download video
                print(f"      Scene {i+1}/{num_scenes}: Downloading video...")
                video_bytes = await self.sora_client.download_video(completed['video_url'])

                # Save to storage
                video_path = await self.storage.save_clip(
                    clip_bytes=video_bytes,
                    video_id=video_id,
                    clip_number=i + 1
                )

                video_paths.append(video_path)
                total_cost += result['cost_usd']

                print(f"      Scene {i+1}/{num_scenes}: ✅ Saved to {video_path}")

            except Exception as e:
                print(f"      Scene {i+1}/{num_scenes}: ❌ Failed - {str(e)}")
                failed_scenes.append({
                    "scene_number": i + 1,
                    "prompt": prompt,
                    "error": str(e)
                })
                # Continue with remaining scenes

        print(f"   ✅ Generated and saved {len(video_paths)}/{num_scenes} videos")
        print(f"   💰 Cost: ${total_cost:.2f}")

        if failed_scenes:
            print(f"   ⚠️  {len(failed_scenes)} scenes failed to generate")

        return {
            "video_paths": video_paths,
            "scene_descriptions": scene_descriptions[:num_scenes],
            "video_prompts": video_prompts,
            "num_videos": len(video_paths),
            "num_failed": len(failed_scenes),
            "failed_scenes": failed_scenes,
            "cost_usd": total_cost,
            "duration_seconds": int(duration),
            "aspect_ratio": aspect_ratio
        }

    async def _enhance_for_video(self, scene_descriptions: List[str]) -> List[str]:
        """
        Enhance scene descriptions for Sora 2 video generation.

        Sora 2 works best with descriptive prompts that include:
        - Action/movement
        - Camera angles
        - Lighting/atmosphere
        - Emotional tone

        Args:
            scene_descriptions: Basic scene descriptions

        Returns:
            Enhanced video prompts
        """
        print(f"      Enhancing {len(scene_descriptions)} descriptions...")

        prompt = f"""You are an expert at writing video generation prompts for Sora 2 (OpenAI's AI video model).

Given these scene descriptions for a video, enhance each one to work perfectly with Sora 2.

**IMPORTANT GUIDELINES:**
- Add dynamic movement and action (camera pans, subjects moving)
- Specify camera angles and movements (close-up, tracking shot, etc.)
- Include lighting and atmosphere details (cinematic, natural light, etc.)
- Add emotional tone and pacing
- Keep prompts clear and descriptive (2-3 sentences max)
- Focus on visual elements that translate well to short video clips
- Avoid static scenes - always include some form of motion

**Original Scene Descriptions:**
{chr(10).join([f"{i+1}. {desc}" for i, desc in enumerate(scene_descriptions)])}

**Your Task:**
Return ONLY a JSON array of enhanced video prompts, one for each scene.
Format: ["enhanced prompt 1", "enhanced prompt 2", ...]

Example Enhancement:
Original: "A person working at a computer"
Enhanced: "A professional working at a modern desk, typing on a laptop. Camera slowly pushes in from medium to close-up shot. Natural daylight streams through a nearby window, creating a focused, productive atmosphere. Subtle head movements and hand gestures as they work."
"""

        try:
            enhanced_prompts = await self.openai_client.generate_completion(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.7,
                response_format="json_object"
            )

            # Parse JSON response
            import json
            parsed = json.loads(enhanced_prompts)

            # Handle different possible JSON formats
            if isinstance(parsed, dict):
                if "prompts" in parsed:
                    result = parsed["prompts"]
                elif "enhanced_prompts" in parsed:
                    result = parsed["enhanced_prompts"]
                elif "scenes" in parsed:
                    result = parsed["scenes"]
                else:
                    # Try to extract first list value
                    result = next(iter(parsed.values()))
            else:
                result = parsed

            if len(result) != len(scene_descriptions):
                print(f"      ⚠️  Enhancement returned {len(result)} prompts, expected {len(scene_descriptions)}")
                # Fall back to original descriptions if mismatch
                return scene_descriptions

            return result

        except Exception as e:
            print(f"      ⚠️  Enhancement failed: {str(e)}, using original descriptions")
            return scene_descriptions
