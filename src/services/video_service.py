"""Video generation service orchestrating the complete pipeline."""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents import ScriptAgent, VoiceAgent, VisualAgent, AssemblyAgent
from src.models.database import Video, CostTracking, VideoStatus
from src.config import settings


class VideoService:
    """Service for orchestrating the 6-phase video generation pipeline."""

    def __init__(self):
        """Initialize video service with all agents."""
        self.script_agent = ScriptAgent()
        self.voice_agent = VoiceAgent()
        self.visual_agent = VisualAgent()
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

        # Create database record
        video = Video(
            uuid=video_id,
            user_id=user_id,
            topic=topic,
            script="",
            status=VideoStatus.PROCESSING,
            duration=duration,
            cost_usd=0.0,
            metadata_={
                "style": style,
                "niche": niche,
                "num_scenes": num_scenes,
                "brand_voice": brand_voice
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
            video.metadata_["script_structure"] = {
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
            video.metadata_["audio"] = {
                "path": audio_path,
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
            video.metadata_["images"] = {
                "paths": image_paths,
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
            video.video_path = video_path
            video.thumbnail_path = image_paths[0]  # Use first image as thumbnail
            video.status = VideoStatus.COMPLETED
            video.cost_usd = total_cost
            video.metadata_["assembly"] = assembly_data["metadata"]
            await db.commit()

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
                    "assembly_cost": assembly_cost,
                    "breakdown": {
                        "gpt4o": script_cost,
                        "elevenlabs": voice_cost,
                        "dalle3": visual_cost,
                        "ffmpeg": assembly_cost
                    }
                }
            )
            db.add(cost_record)
            await db.commit()

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
                "video_id": video_id,
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
                    "script_structure": video.metadata_["script_structure"],
                    "audio": video.metadata_["audio"],
                    "images": video.metadata_["images"],
                    "assembly": video.metadata_["assembly"]
                }
            }

        except Exception as e:
            # Update database with failure
            video.status = VideoStatus.FAILED
            video.metadata_["error"] = str(e)
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

            # Create database record
            video = Video(
                uuid=video_id,
                user_id=user_id,
                topic=topic,
                script="",
                status=VideoStatus.PROCESSING,
                duration=duration,
                cost_usd=0.0,
                metadata_={
                    "style": style,
                    "niche": niche,
                    "num_scenes": num_scenes,
                    "brand_voice": brand_voice
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
            video.metadata_["error"] = str(e)
            await db.commit()

            yield format_sse("error", f'{{"message": "{str(e)}"}}')
            raise
