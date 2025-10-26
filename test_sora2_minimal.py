"""Minimal test for Sora 2 API - simplest prompt."""
import asyncio
from src.integrations.sora2_client import Sora2Client


async def test_minimal():
    """Test Sora 2 with minimal prompt."""
    client = Sora2Client()

    print("="*60)
    print("🧪 MINIMAL SORA 2 TEST")
    print("="*60)

    # Simplest possible prompt
    prompt = "A cat sitting"

    print(f"\n📹 Generating video...")
    print(f"   Prompt: '{prompt}'")
    print(f"   Duration: 10s")
    print(f"   Aspect: portrait")

    try:
        # Create task
        result = await client.generate_video(
            prompt=prompt,
            aspect_ratio="portrait",
            duration="10",
            remove_watermark=True
        )

        print(f"\n✅ Task created!")
        print(f"   Task ID: {result['task_id']}")
        print(f"   Cost: ${result['cost_usd']:.2f}")

        # Wait with shorter timeout (5 minutes)
        print(f"\n⏳ Waiting (max 5 minutes)...")

        completed = await client.wait_for_completion(
            task_id=result['task_id'],
            max_wait_seconds=300,  # 5 minutes instead of 10
            poll_interval=10  # Check every 10 seconds
        )

        print(f"\n✅ SUCCESS!")
        print(f"   Video URL: {completed['video_url']}")
        print(f"   Generation time: {completed.get('cost_time', 'N/A')}s")
        print(f"\n{'='*60}")

        return completed

    except Exception as e:
        print(f"\n❌ Failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(test_minimal())
