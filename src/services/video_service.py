"""Video generation service orchestrating the complete pipeline."""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents import ScriptAgent, VoiceAgent, VisualAgent, VideoAgent, AssemblyAgent
from src.models.database import Video, CostTracking, VideoStatus
from src.config import settings


class VideoService:
    """Service for orchestrating the 6-phase video generation pipeline."""

    def __init__(self):
        """Initialize video service with all agents."""
        self.script_agent = ScriptAgent()
        self.voice_agent = VoiceAgent()
        self.visual_agent = VisualAgent()
        self.video_agent = VideoAgent()
        self.assembly_agent = AssemblyAgent()

    async def generate_video(
        self,
        topic: str,
        db: AsyncSession,
        user_id: Optional[int] = None,
        style: str = "educational",
        niche: str = "finance",
        duration: int = 60,
        num_scenes: int = 6,
        brand_voice: str = "Professional yet conversational"
    ) -> Dict[str, Any]:
        """
        Generate complete video through 6-phase pipeline.

        Args:
            topic: Video topic/subject
            db: Database session
            user_id: Optional user ID
            style: Script style (educational, entertaining, etc.)
            niche: Content niche (finance, tech, etc.)
            duration: Target duration in seconds
            num_scenes: Number of scenes/images
            brand_voice: Brand voice guidelines

        Returns:
            Complete video data with paths, metadata, and costs

        Raises:
            Exception: If any pipeline phase fails
        """
        video_id = str(uuid.uuid4())
        total_cost = 0.0

        print(f"\n{'='*60}")
        print(f"🎬 AI VIDEO GENERATION PIPELINE")
        print(f"{'='*60}")
        print(f"📋 Video ID: {video_id}")
        print(f"📝 Topic: {topic}")
        print(f"⏱️  Duration: {duration}s | Scenes: {num_scenes}")
        print(f"{'='*60}\n")

        # Create database record (id is auto-generated UUID)
        video = Video(
            user_id=user_id,
            topic=topic,
            niche=niche,
            target_duration=duration,
            script="",
            status=VideoStatus.PROCESSING,
            processing_steps={
                "style": style,
                "num_scenes": num_scenes,
                "brand_voice": brand_voice,
                "video_id": video_id  # Store our generated ID in metadata
            }
        )
        db.add(video)
        await db.commit()

        try:
            # Phase 1: Script Generation
            print(f"📝 PHASE 1/6: Script Generation")
            print(f"{'─'*60}")
            script_data = await self.script_agent.generate_script(
                topic=topic,
                style=style,
                duration=duration,
                niche=niche,
                brand_voice=brand_voice
            )
            script = script_data["full_script"]
            script_cost = script_data["_meta"]["cost_usd"]
            total_cost += script_cost
            print(f"✅ Script complete (${script_cost:.4f})\n")

            # Update database
            video.script = script
            video.script_metadata = {
                "hook": script_data["hook"],
                "value_prop": script_data["value_prop"],
                "main_content": script_data["main_content"],
                "cta": script_data["cta"],
                "word_count": script_data.get("estimated_word_count", 0)
            }
            await db.commit()

            # Phase 2: Voice Synthesis
            print(f"🎤 PHASE 2/6: Voice Synthesis")
            print(f"{'─'*60}")
            voice_data = await self.voice_agent.synthesize_voiceover(
                script=script,
                video_id=video_id
            )
            audio_path = voice_data["audio_path"]
            voice_cost = voice_data["cost_usd"]
            total_cost += voice_cost
            print(f"✅ Voice complete (${voice_cost:.4f})\n")

            # Update database
            video.voiceover_url = audio_path
            video.processing_steps["audio"] = {
                "voice_id": voice_data["voice_id"],
                "character_count": voice_data["character_count"],
                "settings": voice_data["settings"]
            }
            await db.commit()

            # Phase 3: Visual Generation
            print(f"🎨 PHASE 3/6: Visual Generation")
            print(f"{'─'*60}")
            visual_data = await self.visual_agent.generate_scene_images(
                script=script,
                video_id=video_id,
                num_scenes=num_scenes
            )
            image_paths = visual_data["image_paths"]
            visual_cost = visual_data["cost_usd"]
            total_cost += visual_cost
            print(f"✅ Visuals complete (${visual_cost:.4f})\n")

            # Update database
            video.scene_images = image_paths
            video.processing_steps["images"] = {
                "scene_descriptions": visual_data["scene_descriptions"],
                "num_images": visual_data["num_images"]
            }
            await db.commit()

            # Phase 4: Video Assembly
            print(f"🎬 PHASE 4/6: Video Assembly")
            print(f"{'─'*60}")
            assembly_data = await self.assembly_agent.assemble_video(
                image_paths=image_paths,
                audio_path=audio_path,
                video_id=video_id,
                duration=duration,
                resolution="1080x1920"  # 9:16 vertical for shorts
            )
            video_path = assembly_data["video_path"]
            assembly_cost = assembly_data["cost_usd"]  # FFmpeg is free!
            total_cost += assembly_cost
            print(f"✅ Assembly complete (${assembly_cost:.4f})\n")

            # Update database with final video
            video.video_url = video_path
            video.thumbnail_url = image_paths[0]  # Use first image as thumbnail
            video.status = VideoStatus.COMPLETED
            video.processing_steps["assembly"] = assembly_data["metadata"]
            video.processing_steps["total_cost_usd"] = total_cost
            await db.commit()

            # Cost tracking is stored in processing_steps for now
            # TODO: Update CostTracking model to support per-video tracking

            # Phase 5 & 6: Publishing (placeholder for future)
            print(f"📤 PHASE 5/6: Publishing (Manual)")
            print(f"{'─'*60}")
            print(f"⏳ Publishing will be added in Phase 4 of MVP\n")

            print(f"🎉 PHASE 6/6: Analytics (Manual)")
            print(f"{'─'*60}")
            print(f"⏳ Analytics will be added in Phase 4 of MVP\n")

            # Final summary
            print(f"\n{'='*60}")
            print(f"✅ VIDEO GENERATION COMPLETE")
            print(f"{'='*60}")
            print(f"📊 Cost Breakdown:")
            print(f"   Script (GPT-4o):     ${script_cost:.4f}")
            print(f"   Voice (ElevenLabs):  ${voice_cost:.4f}")
            print(f"   Images (DALL-E 3):   ${visual_cost:.4f}")
            print(f"   Assembly (FFmpeg):   ${assembly_cost:.4f}")
            print(f"   {'─'*56}")
            print(f"   TOTAL:               ${total_cost:.4f}")
            print(f"{'='*60}")
            print(f"🎞️  Video: {video_path}")
            print(f"🖼️  Thumbnail: {image_paths[0]}")
            print(f"🆔 UUID: {video_id}")
            print(f"{'='*60}\n")

            return {
                "video_id": str(video.id),  # Use database UUID
                "video_path": video_path,
                "thumbnail_path": image_paths[0],
                "duration": assembly_data["metadata"].get("duration", duration),
                "script": script,
                "audio_path": audio_path,
                "image_paths": image_paths,
                "cost_usd": total_cost,
                "cost_breakdown": {
                    "script": script_cost,
                    "voice": voice_cost,
                    "visual": visual_cost,
                    "assembly": assembly_cost
                },
                "metadata": {
                    "script_structure": video.script_metadata,
                    "audio": video.processing_steps.get("audio", {}),
                    "images": video.processing_steps.get("images", {}),
                    "assembly": video.processing_steps.get("assembly", {})
                }
            }

        except Exception as e:
            # Update database with failure
            video.status = VideoStatus.FAILED
            video.error_message = str(e)
            await db.commit()

            print(f"\n❌ VIDEO GENERATION FAILED")
            print(f"{'='*60}")
            print(f"Error: {str(e)}")
            print(f"{'='*60}\n")

            raise Exception(f"Video generation failed: {str(e)}")

    async def generate_video_stream(
        self,
        topic: str,
        db: AsyncSession,
        user_id: Optional[int] = None,
        style: str = "educational",
        niche: str = "finance",
        duration: int = 60,
        num_scenes: int = 6,
        brand_voice: str = "Professional yet conversational"
    ) -> AsyncGenerator[str, None]:
        """
        Generate video with SSE streaming for real-time progress updates.

        Yields:
            SSE-formatted progress messages

        Raises:
            Exception: If any pipeline phase fails
        """
        video_id = str(uuid.uuid4())
        total_cost = 0.0

        def format_sse(event: str, data: Any) -> str:
            """Format data as Server-Sent Event."""
            return f"event: {event}\ndata: {data}\n\n"

        try:
            yield format_sse("start", f'{{"video_id": "{video_id}", "topic": "{topic}"}}')

            # Create database record (id is auto-generated UUID)
            video = Video(
                user_id=user_id,
                topic=topic,
                niche=niche,
                target_duration=duration,
                script="",
                status=VideoStatus.PROCESSING,
                processing_steps={
                    "style": style,
                    "num_scenes": num_scenes,
                    "brand_voice": brand_voice,
                    "video_id": video_id  # Store our generated ID in metadata
                }
            )
            db.add(video)
            await db.commit()

            # Phase 1: Script
            yield format_sse("phase", '{{"phase": 1, "name": "Script Generation", "status": "processing"}}')
            script_data = await self.script_agent.generate_script(
                topic=topic, style=style, duration=duration,
                niche=niche, brand_voice=brand_voice
            )
            script = script_data["full_script"]
            script_cost = script_data["_meta"]["cost_usd"]
            total_cost += script_cost
            video.script = script
            video.metadata_["script_structure"] = {
                "hook": script_data["hook"],
                "value_prop": script_data["value_prop"],
                "main_content": script_data["main_content"],
                "cta": script_data["cta"],
                "word_count": script_data.get("estimated_word_count", 0)
            }
            await db.commit()
            yield format_sse("phase", f'{{"phase": 1, "name": "Script Generation", "status": "completed", "cost": {script_cost}}}')

            # Phase 2: Voice
            yield format_sse("phase", '{{"phase": 2, "name": "Voice Synthesis", "status": "processing"}}')
            voice_data = await self.voice_agent.synthesize_voiceover(
                script=script, video_id=video_id
            )
            audio_path = voice_data["audio_path"]
            voice_cost = voice_data["cost_usd"]
            total_cost += voice_cost
            video.metadata_["audio"] = {
                "path": audio_path,
                "voice_id": voice_data["voice_id"],
                "character_count": voice_data["character_count"],
                "settings": voice_data["settings"]
            }
            await db.commit()
            yield format_sse("phase", f'{{"phase": 2, "name": "Voice Synthesis", "status": "completed", "cost": {voice_cost}}}')

            # Phase 3: Visual
            yield format_sse("phase", '{{"phase": 3, "name": "Visual Generation", "status": "processing"}}')
            visual_data = await self.visual_agent.generate_scene_images(
                script=script, video_id=video_id, num_scenes=num_scenes
            )
            image_paths = visual_data["image_paths"]
            visual_cost = visual_data["cost_usd"]
            total_cost += visual_cost
            video.metadata_["images"] = {
                "paths": image_paths,
                "scene_descriptions": visual_data["scene_descriptions"],
                "num_images": visual_data["num_images"]
            }
            await db.commit()
            yield format_sse("phase", f'{{"phase": 3, "name": "Visual Generation", "status": "completed", "cost": {visual_cost}}}')

            # Phase 4: Assembly
            yield format_sse("phase", '{{"phase": 4, "name": "Video Assembly", "status": "processing"}}')
            assembly_data = await self.assembly_agent.assemble_video(
                image_paths=image_paths, audio_path=audio_path,
                video_id=video_id, duration=duration, resolution="1080x1920"
            )
            video_path = assembly_data["video_path"]
            assembly_cost = assembly_data["cost_usd"]
            total_cost += assembly_cost
            video.video_path = video_path
            video.thumbnail_path = image_paths[0]
            video.status = VideoStatus.COMPLETED
            video.cost_usd = total_cost
            video.metadata_["assembly"] = assembly_data["metadata"]
            await db.commit()
            yield format_sse("phase", f'{{"phase": 4, "name": "Video Assembly", "status": "completed", "cost": {assembly_cost}}}')

            # Track costs
            cost_record = CostTracking(
                video_id=video.id,
                operation="video_generation",
                provider="multi",
                cost_usd=total_cost,
                metadata_={
                    "script_cost": script_cost,
                    "voice_cost": voice_cost,
                    "visual_cost": visual_cost,
                    "assembly_cost": assembly_cost
                }
            )
            db.add(cost_record)
            await db.commit()

            # Complete
            yield format_sse("complete", f'{{"video_id": "{video_id}", "video_path": "{video_path}", "cost": {total_cost}}}')

        except Exception as e:
            # Update database with failure
            video.status = VideoStatus.FAILED
            video.error_message = str(e)
            await db.commit()

            yield format_sse("error", f'{{"message": "{str(e)}"}}')
            raise

    async def generate_video_sora2(
        self,
        topic: str,
        db: AsyncSession,
        user_id: Optional[int] = None,
        style: str = "educational",
        niche: str = "tech",
        duration: int = 60,
        num_scenes: int = 6,
        brand_voice: str = "Professional yet conversational",
        clip_duration: str = "10",
        aspect_ratio: str = "portrait"
    ) -> Dict[str, Any]:
        """
        Generate complete video using Sora 2 for video clips instead of static images.

        NOTE: Due to kie.ai API limitations, video URLs must be manually extracted from dashboard.

        Args:
            topic: Video topic/subject
            db: Database session
            user_id: Optional user ID
            style: Script style (educational, entertaining, etc.)
            niche: Content niche (finance, tech, etc.)
            duration: Target duration in seconds
            num_scenes: Number of Sora 2 video clips
            brand_voice: Brand voice guidelines
            clip_duration: Sora 2 clip duration ("10" or "15" seconds)
            aspect_ratio: Video aspect ratio ("portrait" or "landscape")

        Returns:
            Complete video data with paths, metadata, and costs

        Raises:
            Exception: If any pipeline phase fails
        """
        video_id = str(uuid.uuid4())
        total_cost = 0.0

        print(f"\n{'='*60}")
        print(f"🎬 AI VIDEO GENERATION PIPELINE (SORA 2)")
        print(f"{'='*60}")
        print(f"📋 Video ID: {video_id}")
        print(f"📝 Topic: {topic}")
        print(f"⏱️  Duration: {duration}s | Clips: {num_scenes}")
        print(f"🎥 Sora 2: {clip_duration}s clips, {aspect_ratio} aspect ratio")
        print(f"{'='*60}\n")

        # Create database record
        video = Video(
            user_id=user_id,
            topic=topic,
            niche=niche,
            target_duration=duration,
            script="",
            status=VideoStatus.PROCESSING,
            processing_steps={
                "style": style,
                "num_scenes": num_scenes,
                "brand_voice": brand_voice,
                "video_id": video_id,
                "sora2": True,
                "clip_duration": clip_duration,
                "aspect_ratio": aspect_ratio
            }
        )
        db.add(video)
        await db.commit()

        try:
            # Phase 1: Script Generation
            print(f"📝 PHASE 1/4: Script Generation")
            print(f"{'─'*60}")
            script_data = await self.script_agent.generate_script(
                topic=topic,
                style=style,
                duration=duration,
                niche=niche,
                brand_voice=brand_voice
            )
            script = script_data["full_script"]
            script_cost = script_data["_meta"]["cost_usd"]
            total_cost += script_cost
            print(f"✅ Script complete (${script_cost:.4f})\n")

            # Update database
            video.script = script
            video.script_metadata = {
                "hook": script_data["hook"],
                "value_prop": script_data["value_prop"],
                "main_content": script_data["main_content"],
                "cta": script_data["cta"],
                "word_count": script_data.get("estimated_word_count", 0)
            }
            await db.commit()

            # Phase 2: Voice Synthesis
            print(f"🎤 PHASE 2/4: Voice Synthesis")
            print(f"{'─'*60}")
            voice_data = await self.voice_agent.synthesize_voiceover(
                script=script,
                video_id=video_id
            )
            audio_path = voice_data["audio_path"]
            voice_cost = voice_data["cost_usd"]
            total_cost += voice_cost
            print(f"✅ Voice complete (${voice_cost:.4f})\n")

            # Update database
            video.voiceover_url = audio_path
            video.processing_steps["audio"] = {
                "voice_id": voice_data["voice_id"],
                "character_count": voice_data["character_count"],
                "settings": voice_data["settings"]
            }
            await db.commit()

            # Phase 3: Sora 2 Video Generation
            print(f"🎥 PHASE 3/4: Sora 2 Video Generation")
            print(f"{'─'*60}")
            print(f"⚠️  NOTE: Due to kie.ai API limitations, this phase creates tasks")
            print(f"   but cannot retrieve completed videos automatically.")
            print(f"   You must manually extract video URLs from the dashboard.\n")

            video_data = await self.video_agent.generate_scene_videos(
                script=script,
                video_id=video_id,
                num_scenes=num_scenes,
                duration=clip_duration,
                aspect_ratio=aspect_ratio
            )

            # Check if we got any videos
            if not video_data.get("video_paths"):
                print(f"\n⚠️  WARNING: No videos were generated!")
                print(f"   Failed scenes: {video_data.get('num_failed', 0)}/{num_scenes}")
                print(f"   Check SORA2_STATUS.md for workaround instructions.\n")

                raise Exception(
                    f"Sora 2 video generation failed for all {num_scenes} scenes. "
                    "This is likely due to kie.ai API timeout issues. "
                    "See SORA2_STATUS.md for manual workaround."
                )

            video_paths = video_data["video_paths"]
            video_cost = video_data["cost_usd"]
            total_cost += video_cost
            print(f"✅ Sora 2 videos complete: {len(video_paths)}/{num_scenes} (${video_cost:.4f})\n")

            if video_data.get("num_failed", 0) > 0:
                print(f"⚠️  Warning: {video_data['num_failed']} scenes failed to generate")

            # Update database
            video.scene_images = video_paths  # Store video clip paths
            video.processing_steps["sora2_videos"] = {
                "video_prompts": video_data.get("video_prompts", []),
                "scene_descriptions": video_data.get("scene_descriptions", []),
                "num_videos": video_data["num_videos"],
                "num_failed": video_data.get("num_failed", 0),
                "failed_scenes": video_data.get("failed_scenes", [])
            }
            await db.commit()

            # Phase 4: Video Assembly (Concatenate Sora 2 clips)
            print(f"🎬 PHASE 4/4: Video Assembly")
            print(f"{'─'*60}")
            assembly_data = await self.assembly_agent.assemble_video_from_clips(
                video_clip_paths=video_paths,
                audio_path=audio_path,
                video_id=video_id,
                resolution="1080x1920"  # 9:16 vertical for shorts
            )
            video_path = assembly_data["video_path"]
            assembly_cost = assembly_data["cost_usd"]  # FFmpeg is free!
            total_cost += assembly_cost
            print(f"✅ Assembly complete (${assembly_cost:.4f})\n")

            # Update database with final video
            video.video_url = video_path
            video.thumbnail_url = video_paths[0] if video_paths else None
            video.status = VideoStatus.COMPLETED
            video.processing_steps["assembly"] = assembly_data["metadata"]
            video.processing_steps["total_cost_usd"] = total_cost
            await db.commit()

            # Final summary
            print(f"\n{'='*60}")
            print(f"✅ VIDEO GENERATION COMPLETE (SORA 2)")
            print(f"{'='*60}")
            print(f"📊 Cost Breakdown:")
            print(f"   Script (GPT-4o):     ${script_cost:.4f}")
            print(f"   Voice (ElevenLabs):  ${voice_cost:.4f}")
            print(f"   Videos (Sora 2):     ${video_cost:.4f}")
            print(f"   Assembly (FFmpeg):   ${assembly_cost:.4f}")
            print(f"   {'─'*56}")
            print(f"   TOTAL:               ${total_cost:.4f}")
            print(f"{'='*60}")
            print(f"🎞️  Video: {video_path}")
            print(f"🎥 Clips: {len(video_paths)} Sora 2 videos")
            print(f"🆔 UUID: {video_id}")
            print(f"{'='*60}\n")

            return {
                "video_id": str(video.id),
                "video_path": video_path,
                "thumbnail_path": video_paths[0] if video_paths else None,
                "duration": assembly_data["metadata"].get("duration", duration),
                "script": script,
                "audio_path": audio_path,
                "video_clip_paths": video_paths,
                "num_clips": len(video_paths),
                "num_failed": video_data.get("num_failed", 0),
                "cost_usd": total_cost,
                "cost_breakdown": {
                    "script": script_cost,
                    "voice": voice_cost,
                    "video": video_cost,
                    "assembly": assembly_cost
                },
                "metadata": {
                    "script_structure": video.script_metadata,
                    "audio": video.processing_steps.get("audio", {}),
                    "sora2_videos": video.processing_steps.get("sora2_videos", {}),
                    "assembly": video.processing_steps.get("assembly", {})
                }
            }

        except Exception as e:
            # Update database with failure
            video.status = VideoStatus.FAILED
            video.error_message = str(e)
            await db.commit()

            print(f"\n❌ VIDEO GENERATION FAILED (SORA 2)")
            print(f"{'='*60}")
            print(f"Error: {str(e)}")
            print(f"{'='*60}\n")

            raise Exception(f"Sora 2 video generation failed: {str(e)}")
