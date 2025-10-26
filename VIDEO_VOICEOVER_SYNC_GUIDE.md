# Video-Voiceover Sync System

## Problem Statement

When generating AI videos with Sora 2, a common issue is **video-voiceover mismatch**:
- Videos show generic visuals that don't match what's being said
- Timing is off - video clips may be too long or short for the audio
- Content feels "boring" because visuals are disconnected from narration

## Root Cause

Sora 2 video generation and ElevenLabs audio generation are **independent processes**:
1. Script is generated with generic scene descriptions
2. Audio is created from the full script
3. Videos are generated from scene descriptions (without knowing audio content/timing)
4. Result: Video shows one thing, audio says something else

## Solution: Timestamp-Based Sync System

This system coordinates video generation with precise voiceover timing for better sync.

### How It Works

```
1. Generate script with TIMESTAMPS
   ├─ Break into 8-12 second segments
   ├─ Each segment has: start time, end time, text, visual description
   └─ Example: {"start": 0, "end": 10, "text": "...", "visual": "...", "word_count": 25}

2. Generate audio from segments
   ├─ Create voiceover for each segment
   ├─ Measure ACTUAL audio duration using ffprobe
   └─ Return: audio bytes + actual duration (e.g., 9.2 seconds)

3. Generate Sora 2 videos matched to audio
   ├─ Use visual description from corresponding segment
   ├─ Set clip duration based on audio duration (10s or 15s)
   └─ Video content now matches what's being said in that segment
```

### Benefits

✅ **Better Sync**: Video content matches what the voiceover is saying
✅ **Precise Timing**: Sora 2 clips generated at correct durations
✅ **Less Boring**: Visuals are contextually relevant to narration
✅ **Higher Quality**: Professional feel with coordinated content

---

## Implementation

### 1. Script Generation with Timestamps

**File**: `src/integrations/openai_client.py`

```python
# Generate script with timestamps
script_data = await openai_client.generate_script(
    topic="5 ways to save $1000 in 30 days",
    style="educational",
    duration=60,
    brand_voice="Professional yet conversational",
    niche="finance",
    include_timestamps=True  # ← Enable timestamp mode
)

# Result:
{
  "full_script": "...",
  "segments": [
    {
      "start": 0,
      "end": 10,
      "text": "Want to save $1000 fast? Here's tip number one...",
      "visual": "Piggy bank with $1000 goal counter, animated savings growth",
      "word_count": 18
    },
    {
      "start": 10,
      "end": 20,
      "text": "Cut your subscription services. Most people waste...",
      "visual": "Smartphone showing subscription apps, cancel buttons highlighted",
      "word_count": 22
    }
    // ... more segments
  ]
}
```

**Key Features**:
- `include_timestamps=True` activates segment-based generation
- Each segment is 8-12 seconds (optimal for Sora 2)
- Visual descriptions are specific to what's being said
- Word count helps estimate audio duration

### 2. Audio Generation with Duration Tracking

**File**: `src/integrations/elevenlabs_client.py`

```python
# Generate audio segments with timing
audio_segments = await elevenlabs_client.synthesize_segments(
    segments=script_data['segments'],
    voice_id="21m00Tcm4TlvDq8ikWAM"  # Rachel voice
)

# Result:
[
  {
    "audio_bytes": b"...",
    "text": "Want to save $1000 fast? Here's tip number one...",
    "duration_seconds": 9.2,  # ← Actual measured duration
    "segment_index": 0,
    "planned_start": 0,
    "planned_end": 10
  },
  {
    "audio_bytes": b"...",
    "text": "Cut your subscription services...",
    "duration_seconds": 11.5,  # ← Actual measured duration
    "segment_index": 1,
    "planned_start": 10,
    "planned_end": 20
  }
  // ... more segments
]
```

**How Duration is Measured**:
1. Generate audio with ElevenLabs
2. Save to temporary file
3. Use ffprobe to get exact duration:
   ```bash
   ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 audio.mp3
   ```
4. Fallback: Estimate from word count (150 words/min = 2.5 words/sec)

### 3. Video Generation with Segment Matching

**File**: `src/agents/video_agent.py`

```python
# Generate Sora 2 videos matched to audio segments
result = await video_agent.generate_scene_videos(
    script=script_data['full_script'],
    video_id="video-uuid-here",
    num_scenes=6,
    duration="10",
    aspect_ratio="portrait",
    character_style=CharacterStyle.NO_FACE,
    script_segments=audio_segments  # ← Pass audio segments
)
```

**What Happens**:
1. Uses `visual` description from each segment (matches audio content)
2. Determines clip duration based on audio duration:
   - Audio 12+ seconds → Sora 2 generates 15s clip
   - Audio <12 seconds → Sora 2 generates 10s clip
3. Clips are trimmed/extended to match exact audio duration during assembly

**Example Log Output**:
```
🎬 Generating 6 scene videos
   🎭 Character Style: no_face
   🏷️  Topic Category: money_saving
   📝 Creating scene descriptions...
   🎯 Using 6 timestamped segments for precise sync
   ✨ Enhancing descriptions with brand character...
   🎥 Generating Sora 2 videos (this may take 2-4 minutes per video)...
      Scene 1/6: Using 10s based on 9.2s audio
      Scene 2/6: Using 15s based on 11.5s audio
      Scene 3/6: Using 10s based on 8.7s audio
      ...
```

---

## Comparison: Before vs After

### Before (Generic Sync)

```
Script:
"Want to save $1000 fast? Here's tip number one: cut subscriptions."

Video Prompt:
"Professional motion graphics showing money-saving concepts with charts"

Result:
❌ Video shows generic money charts
❌ Audio talks about subscriptions
❌ Disconnect = boring and confusing
```

### After (Timestamp-Based Sync)

```
Script Segment 1:
{
  "start": 0,
  "end": 10,
  "text": "Want to save $1000 fast? Here's tip number one: cut subscriptions.",
  "visual": "Smartphone showing subscription apps with cancel buttons highlighted, money saved counter"
}

Audio:
- Duration: 9.2 seconds (measured)

Video Prompt:
"No human presenter. Smartphone showing subscription apps with cancel buttons highlighted, money saved counter animating upward. Clean animations with navy blue and gold color scheme."

Result:
✅ Video shows exactly what audio describes (subscriptions)
✅ Duration matches (10s video for 9.2s audio)
✅ Engaging and professional sync
```

---

## API Usage

### Option 1: Automatic Timestamp Mode

```bash
curl -X POST http://localhost:8000/api/video/generate-sora2 \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "5 ways to save $1000 in 30 days",
    "niche": "finance",
    "num_scenes": 6,
    "character_style": "no_face",
    "enable_timestamp_sync": true  # ← Enable better sync
  }'
```

**What Happens**:
1. Script generated with timestamps
2. Audio generated per segment with duration tracking
3. Sora 2 videos matched to segment content and timing
4. Final video assembled with precise sync

### Option 2: Manual Control

```python
# 1. Generate timestamped script
script = await openai_client.generate_script(
    topic="...",
    include_timestamps=True
)

# 2. Generate audio segments
audio_segments = await elevenlabs_client.synthesize_segments(
    segments=script['segments']
)

# 3. Generate matching videos
videos = await video_agent.generate_scene_videos(
    script=script['full_script'],
    script_segments=audio_segments
)

# 4. Assemble final video
# (implementation in VideoService)
```

---

## Technical Details

### Timestamp Format

```json
{
  "start": 0,          // Planned start time in seconds
  "end": 10,           // Planned end time in seconds
  "text": "...",       // Narration text for this segment
  "visual": "...",     // Visual description for Sora 2
  "word_count": 25     // Word count for duration estimation
}
```

### Audio Segment Format

```json
{
  "audio_bytes": "b'...'",
  "text": "...",
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "character_count": 125,
  "cost_usd": 0.0375,
  "segment_index": 0,
  "duration_seconds": 9.2,    // ← Actual measured duration
  "planned_start": 0,
  "planned_end": 10
}
```

### Duration Determination Logic

```python
# Round to nearest supported Sora 2 duration
if segment_duration > 12:
    sora_duration = "15"  # 15 seconds
else:
    sora_duration = "10"  # 10 seconds

# Later: trim/extend to exact audio duration during FFmpeg assembly
```

---

## Configuration

### Enable for All Videos (Default)

**File**: `src/config.py`

```python
# Video-Voiceover Sync
ENABLE_TIMESTAMP_SYNC: bool = True  # Use timestamp-based sync by default
DEFAULT_SEGMENT_DURATION: int = 10  # Target segment length in seconds
```

### Per-Request Control

```python
# Disable timestamp sync for specific video
result = await video_service.generate_video_sora2(
    topic="...",
    enable_timestamp_sync=False  # Use old generic sync
)
```

---

## Troubleshooting

### Issue: Videos still don't match audio

**Possible Causes**:
1. `script_segments` not passed to `generate_scene_videos()`
2. Visual descriptions too generic
3. Brand character prompt overriding segment visuals

**Solutions**:
1. Verify `script_segments` parameter is provided
2. Check logs for "Using N timestamped segments" message
3. Ensure visual descriptions are specific and actionable

### Issue: Audio duration mismatch

**Possible Causes**:
1. ffprobe not installed or not in PATH
2. Falling back to word-count estimation (less accurate)

**Solutions**:
1. Install FFmpeg: `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Linux)
2. Verify: `which ffprobe` should return a path
3. Check logs for "Using {duration}s based on {audio_duration}s audio"

### Issue: Videos too long/short

**Possible Causes**:
1. Sora 2 only supports 10s or 15s durations
2. No post-processing to trim to exact duration

**Solutions**:
1. Expect some variance (10s video for 9.2s audio is normal)
2. Future: Implement FFmpeg trimming to exact duration
3. Use crossfade transitions to hide timing gaps

---

## Future Enhancements

### Planned Features

1. **Exact Duration Trimming**: Use FFmpeg to trim Sora 2 clips to exact audio duration
   ```python
   # Trim 10s video to 9.2s
   ffmpeg -i video.mp4 -t 9.2 -c copy trimmed.mp4
   ```

2. **B-Roll Integration**: Use generic Sora 2 clips as B-roll when visual description is vague
   ```python
   if segment_visual_quality < 0.7:
       use_broll_clip()
   ```

3. **Voice Inflection Matching**: Analyze audio for emphasis and match video pacing
   ```python
   # Detect emphasized words
   emphasized_words = analyze_prosody(audio_bytes)

   # Adjust video prompt
   video_prompt += f"Emphasize visuals at: {emphasized_words}"
   ```

4. **Multi-Speaker Support**: Track speaker changes and match character on-screen
   ```python
   # Detect speaker
   if segment['speaker'] == "narrator":
       character_style = CharacterStyle.NO_FACE
   elif segment['speaker'] == "expert":
       character_style = CharacterStyle.PROFESSIONAL_MALE
   ```

---

## Summary

**The timestamp-based sync system solves video-voiceover mismatch by**:

1. ✅ Breaking scripts into precise 8-12 second segments
2. ✅ Generating audio and measuring actual duration
3. ✅ Creating Sora 2 videos matched to specific audio content
4. ✅ Using appropriate clip durations (10s or 15s) based on audio length

**Result**: Professional, engaging videos where visuals match what's being said.

**To Enable**: Add `"enable_timestamp_sync": true` to your API request or set `ENABLE_TIMESTAMP_SYNC=True` in config.
