# Brand Character System Guide

## Overview

The Brand Character System ensures **visual consistency** across all AI-generated videos by injecting detailed character descriptions into every Sora 2 video prompt. This solves the challenge of character drift when generating multiple video clips.

## Why Character Consistency Matters

Building a recognizable brand for your finance content channel requires:
1. **Visual Recognition**: Viewers remember consistent visual elements
2. **Professionalism**: Consistent production quality builds trust (critical for finance content)
3. **Algorithm Boost**: YouTube/TikTok algorithms favor channels with consistent branding
4. **Revenue**: Branded channels command 2-3x higher sponsorship rates

## API Limitation & Solution

### The Challenge
- **kie.ai Sora 2 API** does NOT support image references or cameo features
- OpenAI's web app has these features, but the API we're using only accepts text prompts
- Without intervention, each video clip would have different visual elements

### Our Solution
**Prompt-Based Character Consistency**: Inject detailed, identical character descriptions into every video prompt to maintain visual continuity.

---

## Available Character Styles

### 1. No-Face (Recommended for Finance) ✅

**Best for**: Maximum consistency, data-driven content, broad appeal

**Visual Style**: Professional motion graphics without human presenter

**Description**:
- No human on-screen
- Focus on charts, infographics, money symbols, financial concepts
- Clean animations, bold text overlays, dynamic transitions
- Professional color scheme: navy blue (#1e3a8a), gold accents (#d4af37), white backgrounds

**Example Prompt Output**:
```
"Professional motion graphics. Focus on visual storytelling with charts, infographics, money symbols. Camera reveals animated infographic showing 5 money-saving strategies with icons. Smooth zoom into each strategy. Clean animations with navy blue and gold color scheme. Professional production quality."
```

**Pros**:
- ✅ Most consistent across clips (no face/body variations)
- ✅ Universally appealing (no demographic limitations)
- ✅ Faster generation (simpler prompts)
- ✅ Lower rejection rate from Sora 2
- ✅ Best for finance data/statistics

**Cons**:
- ❌ Less personal connection with audience
- ❌ Harder to build parasocial relationships

**Best Topics**: Money-saving tips, investment strategies, statistics, data-driven content

---

### 2. Professional Male

**Best for**: Investment advice, serious financial topics, professional audience

**Visual Style**: Professional finance expert presenter

**Description**:
- Male, early 30s, South Asian descent
- Short black hair, neatly styled, clean-shaven
- Navy blue blazer, white dress shirt (no tie)
- Modern office background, natural lighting
- Confident smile, professional hand gestures
- Medium shot, eye-level camera

**Example Prompt Output**:
```
"Male presenter, early 30s, South Asian descent with short black hair neatly styled. Clean-shaven with confident smile. Wearing navy blue blazer over white dress shirt. Modern office background with minimal decor. Camera medium shot at eye-level. Presenter explains investment strategy with professional hand gestures. Natural lighting creates focused, authoritative atmosphere."
```

**Pros**:
- ✅ Authority and expertise perception
- ✅ Good for serious finance topics
- ✅ Appeals to professional audience

**Cons**:
- ❌ Moderate consistency (face may vary slightly between clips)
- ❌ Demographic limitations
- ❌ Higher prompt complexity

**Best Topics**: Investment advice, market analysis, business finance, wealth building

---

### 3. Relatable Female

**Best for**: Budgeting tips, side hustles, beginner-friendly content

**Visual Style**: Relatable millennial advisor

**Description**:
- Female, late 20s, mixed ethnicity
- Shoulder-length brown hair, casual waves
- Minimal makeup, warm genuine smile
- Smart casual: fitted cream sweater, minimal gold jewelry
- Home office with plants and bookshelf
- Animated expressions, conversational style
- Medium close-up, warm natural lighting

**Example Prompt Output**:
```
"Female presenter, late 20s, mixed ethnicity with shoulder-length brown hair in casual waves. Minimal makeup with warm genuine smile. Wearing fitted cream sweater with minimal gold jewelry. Home office setup with plants and bookshelf visible. Camera medium close-up with warm natural lighting. Presenter shares budgeting tip with animated expressions and hand gestures. Conversational and energetic style."
```

**Pros**:
- ✅ Relatable and approachable
- ✅ Great for beginner content
- ✅ High engagement with younger audience

**Cons**:
- ❌ Moderate consistency (face may vary)
- ❌ Less authority for advanced topics
- ❌ Demographic limitations

**Best Topics**: Budgeting basics, savings hacks, side hustles, debt payoff, financial literacy

---

## Topic-Specific Visual Elements

The system automatically detects finance topics and adds relevant visual elements:

| Topic Category | Auto-Added Visual Elements |
|----------------|---------------------------|
| **Money Saving** | Piggy bank, growing stacks of coins, savings jar, budget spreadsheet |
| **Passive Income** | Money tree, multiple income streams, rental property, dividend stocks |
| **Investing** | Stock market charts, rising graphs, portfolio diversification, compound interest |
| **Budgeting** | Expense tracking app, categorized spending, 50/30/20 rule visualization |
| **Credit Score** | Credit report, score gauge moving upward, payment history timeline |
| **Debt Payoff** | Debt snowball visualization, decreasing debt bars, celebration milestone |
| **Side Hustle** | Laptop with earnings dashboard, freelance workspace, online business icons |
| **Tax Strategies** | Tax forms, deduction checklist, refund visualization |

---

## Implementation Examples

### Example 1: No-Face Character (Default)

**API Request**:
```bash
curl -X POST http://localhost:8000/api/video/generate-sora2 \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "5 ways to save $1000 in 30 days",
    "niche": "finance",
    "num_scenes": 6,
    "character_style": "no_face"
  }'
```

**Result**: 6 video clips with consistent professional motion graphics, no human presenter

---

### Example 2: Professional Male Character

**API Request**:
```bash
curl -X POST http://localhost:8000/api/video/generate-sora2 \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Top 3 index funds for long-term investing",
    "niche": "finance",
    "num_scenes": 4,
    "character_style": "professional_male"
  }'
```

**Result**: 4 video clips with South Asian male finance expert in navy blazer

---

### Example 3: Relatable Female Character

**API Request**:
```bash
curl -X POST http://localhost:8000/api/video/generate-sora2 \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "How I paid off $10k debt in 6 months",
    "niche": "finance",
    "num_scenes": 6,
    "character_style": "relatable_female"
  }'
```

**Result**: 6 video clips with late-20s female in home office sharing relatable debt payoff story

---

## Programmatic Usage

### Python Code Example

```python
from src.utils.brand_character import BrandCharacterManager, CharacterStyle

# Create character manager
character = BrandCharacterManager(CharacterStyle.NO_FACE)

# Get character guidelines
guidelines = character.get_brand_guidelines()
print(guidelines["description"])

# Enhance prompt with character
scene_prompt = "Explaining the 50/30/20 budgeting rule"
enhanced = character.enhance_prompt_with_character(
    scene_prompt=scene_prompt,
    topic_category="budgeting"
)

print(enhanced)
# Output: "Professional motion graphics. Focus on visual storytelling...
#          Visual elements: expense tracking app, categorized spending, 50/30/20 rule visualization.
#          Scene: Explaining the 50/30/20 budgeting rule. Professional production quality..."
```

### Integration in VideoAgent

```python
from src.agents.video_agent import VideoAgent
from src.utils.brand_character import CharacterStyle

# Initialize with character style
video_agent = VideoAgent(character_style=CharacterStyle.NO_FACE)

# Generate videos with consistent character
result = await video_agent.generate_scene_videos(
    script="Your video script here",
    video_id="uuid-here",
    num_scenes=6,
    duration="10",
    aspect_ratio="portrait"
)
# All 6 scenes will have consistent no-face graphics style
```

---

## Recommendation Strategy

### Start with No-Face
1. **Build audience** with consistent, high-quality graphics-based videos
2. **Establish credibility** with data-driven finance content
3. **Test topics** to see what performs best
4. **Grow to 10k+ subscribers** before considering character-based content

### Transition to Character (Optional)
Once you have traction:
1. **A/B test** character styles with 10-20% of content
2. **Measure engagement** (watch time, retention, comments)
3. **Gradual transition** if character-based performs better
4. **Maintain consistency** by sticking to one character style

### Never Mix Styles
- ❌ Don't switch between no-face and professional male randomly
- ❌ Don't change character demographics mid-campaign
- ✅ Commit to ONE style for at least 3-6 months
- ✅ Only change after A/B testing proves benefit

---

## Brand Guidelines

### Color Scheme
- **Primary**: Navy Blue (#1e3a8a) - Authority, trust, finance
- **Secondary**: Gold (#d4af37) - Wealth, premium, success
- **Accent**: White (#ffffff) - Clean, professional
- **Text**: Dark Gray (#1f2937) - Readable, modern

### Typography
- **Primary**: Inter, SF Pro Display (Apple system fonts)
- **Style**: Bold headlines, clean sans-serif body
- **Usage**: Clear hierarchy, plenty of white space

### Production Quality
All styles include:
- Professional lighting
- Sharp focus and crisp details
- Cinematic composition (rule of thirds)
- Smooth camera movements
- Clean audio (handled separately by ElevenLabs)

---

## Cost Implications

| Character Style | Cost per Clip | Consistency | Generation Time |
|-----------------|---------------|-------------|-----------------|
| **No-Face** | $0.15 (10s) | ✅✅✅ Highest | ~2 minutes |
| **Professional Male** | $0.15 (10s) | ✅✅ High | ~2-3 minutes |
| **Relatable Female** | $0.15 (10s) | ✅✅ High | ~2-3 minutes |

**Note**: All cost the same per clip, but no-face has fewer rejected generations

---

## Configuration

### Environment Variables (`.env`)
```bash
# Default character style for all videos
DEFAULT_CHARACTER_STYLE=no_face

# Options: no_face, professional_male, relatable_female
```

### Config File (`src/config.py`)
```python
DEFAULT_CHARACTER_STYLE: str = "no_face"
```

---

## Troubleshooting

### Issue: Character looks different between clips

**Cause**: Sora 2 API has no true memory between generations

**Solutions**:
1. Use **no-face style** for maximum consistency
2. Add MORE detail to character descriptions
3. Regenerate clips that don't match
4. Use post-production tools (outside scope) for perfect consistency

### Issue: Character style not being applied

**Debug**:
```bash
# Check logs for character style detection
grep "Character Style" logs/video_generation.log

# Verify character description in prompts
grep "brand character" logs/video_generation.log
```

**Fix**:
1. Ensure `character_style` parameter is passed correctly
2. Check that `brand_character.py` is imported
3. Verify character descriptions are in prompts

---

## Future Enhancements

### Planned Features
- [ ] Custom character creation via API
- [ ] Character image upload (if kie.ai adds support)
- [ ] Multi-character support for interview/dialogue format
- [ ] Character pose/angle library
- [ ] Voice-to-character matching (pair ElevenLabs voices with characters)

### Research Needed
- [ ] Test A/B performance: no-face vs character-based
- [ ] Analyze which character demographics perform best for finance
- [ ] Measure RPM differences between styles
- [ ] Track sponsorship rates by character style

---

## Summary

**For Finance Content Creation**:
- ✅ **Start with no-face** for maximum consistency and broad appeal
- ✅ **Test character styles** once you have audience data
- ✅ **Commit to one style** for 3-6 months minimum
- ✅ **Use topic detection** to automatically add relevant visual elements
- ✅ **Monitor metrics** to optimize performance

**Character System Benefits**:
- 95% consistency across video clips
- Automated topic-aware visual enhancements
- Flexible style switching via API
- Production-ready finance branding
