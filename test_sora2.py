"""Quick test for Sora 2 API integration."""
import asyncio
from src.integrations.sora2_client import Sora2Client


async def test_sora2():
    """Test Sora 2 video generation."""
    client = Sora2Client()

    print("="*60)
    print("🧪 TESTING SORA 2 API INTEGRATION")
    print("="*60)

    # Test 1: Generate video
    print("\n📹 Test 1: Generating Sora 2 video...")
    prompt = "A professional giving a presentation about AI technology in a modern office, gesturing enthusiastically"

    try:
        result = await client.generate_video(
            prompt=prompt,
            aspect_ratio="portrait",
            duration="10",
            remove_watermark=True
        )

        print(f"✅ Task created successfully!")
        print(f"   Task ID: {result['task_id']}")
        print(f"   Cost: ${result['cost_usd']:.2f}")
        print(f"   Status: {result['status']}")

        # Test 2: Wait for completion
        print(f"\n⏳ Test 2: Waiting for video generation...")
        print(f"   This may take 2-4 minutes...")

        completed = await client.wait_for_completion(
            task_id=result['task_id'],
            max_wait_seconds=600,
            poll_interval=15
        )

        print(f"\n✅ Video generated successfully!")
        print(f"   Video URL: {completed['video_url']}")
        print(f"   Generation time: {completed['cost_time']}s")

        # Test 3: Download video
        print(f"\n⬇️  Test 3: Downloading video...")
        video_bytes = await client.download_video(completed['video_url'])
        print(f"✅ Downloaded {len(video_bytes):,} bytes")

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print(f"\n🎬 Video URL: {completed['video_url']}")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(test_sora2())
