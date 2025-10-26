"""Sora 2 API client for AI video generation via kie.ai."""
import asyncio
from typing import Dict, Any, Optional, List
import httpx

from src.config import settings


class Sora2Client:
    """Async Sora 2 client wrapper for kie.ai API."""

    def __init__(self):
        """Initialize Sora 2 client."""
        self.api_key = settings.KIE_AI_API_KEY
        self.base_url = "https://api.kie.ai/api/v1"

        # Default settings
        self.default_duration = "10"  # 10 or 15 seconds
        self.default_aspect_ratio = "portrait"  # portrait or landscape
        self.remove_watermark = True

    async def generate_video(
        self,
        prompt: str,
        aspect_ratio: str = "portrait",
        duration: str = "10",
        remove_watermark: bool = True,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt using Sora 2.

        Args:
            prompt: Text description of desired video
            aspect_ratio: "portrait" (9:16) or "landscape" (16:9)
            duration: "10" or "15" seconds
            remove_watermark: Remove watermark from video
            callback_url: Optional callback URL for completion notification

        Returns:
            Task ID and metadata for polling

        Raises:
            Exception: If API request fails
        """
        url = f"{self.base_url}/jobs/createTask"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "sora-2-text-to-video",
            "input": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "n_frames": duration,
                "remove_watermark": remove_watermark
            }
        }

        if callback_url:
            payload["callBackUrl"] = callback_url

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

                result = response.json()

                if result.get("code") != 200:
                    raise Exception(f"Sora 2 API error: {result.get('message', 'Unknown error')}")

                task_id = result["data"]["taskId"]

                # Estimate cost (30 credits = $0.15 per 10s video)
                cost_per_10s = 0.15
                duration_multiplier = 1.5 if duration == "15" else 1.0
                cost_usd = cost_per_10s * duration_multiplier

                return {
                    "task_id": task_id,
                    "model": "sora-2-text-to-video",
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "duration": int(duration),
                    "cost_usd": cost_usd,
                    "status": "processing"
                }

        except httpx.HTTPStatusError as e:
            raise Exception(f"Sora 2 API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Video generation failed: {str(e)}")

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of video generation task.

        Args:
            task_id: Task ID from generate_video

        Returns:
            Task status and video URL when completed

        Raises:
            Exception: If API request fails
        """
        url = f"{self.base_url}/jobs/recordInfo"

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        params = {"taskId": task_id}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()

                result = response.json()

                if result.get("code") != 200:
                    raise Exception(f"Task query error: {result.get('message', 'Unknown error')}")

                data = result.get("data")

                # If data is null, task is still processing
                if data is None:
                    return {
                        "task_id": task_id,
                        "status": "processing"
                    }

                state = data.get("state", "unknown")

                response_data = {
                    "task_id": task_id,
                    "state": state,
                    "model": data.get("model", ""),
                    "create_time": data.get("createTime", 0),
                    "update_time": data.get("updateTime", 0)
                }

                # Map kie.ai state values to our simpler format
                if state == "success":
                    response_data["status"] = "success"
                    # Extract video URL from resultJson
                    result_json_str = data.get("resultJson", "{}")
                    import json
                    result_json = json.loads(result_json_str)
                    result_urls = result_json.get("resultUrls", [])
                    if result_urls:
                        response_data["video_url"] = result_urls[0]
                    response_data["complete_time"] = data.get("completeTime", 0)

                elif state in ["waiting", "queuing", "generating"]:
                    response_data["status"] = "processing"

                elif state == "fail":
                    response_data["status"] = "fail"
                    response_data["error_code"] = data.get("failCode", "")
                    response_data["error_message"] = data.get("failMsg", "Generation failed")

                else:
                    response_data["status"] = "unknown"

                return response_data

        except httpx.HTTPStatusError as e:
            raise Exception(f"Task status query error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Task status check failed: {str(e)}")

    async def wait_for_completion(
        self,
        task_id: str,
        max_wait_seconds: int = 600,
        poll_interval: int = 10
    ) -> Dict[str, Any]:
        """
        Poll task status until completion or timeout.

        Args:
            task_id: Task ID to monitor
            max_wait_seconds: Maximum time to wait (default: 10 minutes)
            poll_interval: Seconds between status checks (default: 10s)

        Returns:
            Final task status with video URL

        Raises:
            Exception: If task fails or times out
        """
        elapsed = 0

        while elapsed < max_wait_seconds:
            status = await self.get_task_status(task_id)

            if status["status"] == "success":
                return status

            elif status["status"] == "fail":
                error_msg = status.get("error_message", "Unknown error")
                raise Exception(f"Video generation failed: {error_msg}")

            # Still processing, wait before next poll
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

            print(f"⏳ Sora 2 generation in progress... ({elapsed}/{max_wait_seconds}s)")

        raise Exception(f"Video generation timed out after {max_wait_seconds}s")

    async def generate_video_batch(
        self,
        prompts: List[str],
        aspect_ratio: str = "portrait",
        duration: str = "10",
        remove_watermark: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple videos in parallel.

        Args:
            prompts: List of video prompts
            aspect_ratio: "portrait" or "landscape"
            duration: "10" or "15" seconds
            remove_watermark: Remove watermark from videos

        Returns:
            List of task IDs and metadata

        Raises:
            Exception: If any API request fails
        """
        tasks = []
        for prompt in prompts:
            task = self.generate_video(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                duration=duration,
                remove_watermark=remove_watermark
            )
            tasks.append(task)

        # Execute all requests in parallel
        results = await asyncio.gather(*tasks)
        return results

    async def download_video(self, video_url: str) -> bytes:
        """
        Download generated video from URL.

        Args:
            video_url: Video URL from task completion

        Returns:
            Video bytes

        Raises:
            Exception: If download fails
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(video_url)
                response.raise_for_status()
                return response.content

        except Exception as e:
            raise Exception(f"Video download failed: {str(e)}")

    def calculate_cost(self, duration: str, num_videos: int = 1) -> float:
        """
        Calculate estimated cost for video generation.

        Args:
            duration: "10" or "15" seconds
            num_videos: Number of videos to generate

        Returns:
            Total cost in USD
        """
        cost_per_10s = 0.15
        duration_multiplier = 1.5 if duration == "15" else 1.0
        return cost_per_10s * duration_multiplier * num_videos
