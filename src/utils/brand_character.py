"""Brand character and visual style management for consistent video generation."""
from typing import Dict, Any, Optional
from enum import Enum


class CharacterStyle(str, Enum):
    """Available brand character styles."""
    NO_FACE = "no_face"  # No human presenter, focus on visuals
    PROFESSIONAL_MALE = "professional_male"  # Male finance expert
    RELATABLE_FEMALE = "relatable_female"  # Female millennial advisor
    CUSTOM = "custom"  # User-defined character


class BrandCharacterManager:
    """Manages consistent brand character across video generations."""

    # Character descriptions for consistency
    CHARACTER_DESCRIPTIONS = {
        CharacterStyle.NO_FACE: {
            "visual_style": "professional motion graphics",
            "description": "No human presenter. Focus on visual storytelling with charts, infographics, money symbols, and financial concepts. Use clean animations, bold text overlays, and dynamic transitions. Professional color scheme: navy blue, gold accents, white backgrounds.",
            "camera_style": "static shots of graphics, smooth transitions between visual elements",
            "suitable_for": ["all finance topics", "data-driven content", "educational explainers"]
        },

        CharacterStyle.PROFESSIONAL_MALE: {
            "visual_style": "professional finance expert",
            "description": "Male presenter, early 30s, South Asian descent with short black hair neatly styled. Clean-shaven with confident smile. Wearing navy blue blazer over white dress shirt (no tie). Modern office background with minimal decor, natural lighting. Speaks directly to camera with professional hand gestures. Approachable yet authoritative demeanor.",
            "camera_style": "medium shot, eye-level, professional lighting setup",
            "suitable_for": ["investment advice", "serious financial topics", "professional audience"]
        },

        CharacterStyle.RELATABLE_FEMALE: {
            "visual_style": "relatable millennial advisor",
            "description": "Female presenter, late 20s, mixed ethnicity with shoulder-length brown hair in casual waves. Minimal makeup with warm genuine smile. Wearing smart casual: fitted cream sweater, minimal gold jewelry. Home office setup with plants and bookshelf visible. Animated expressions, uses visual aids and gestures naturally. Conversational and energetic style.",
            "camera_style": "medium close-up, slightly off-center, warm natural lighting",
            "suitable_for": ["budgeting tips", "side hustles", "beginner-friendly content"]
        }
    }

    # Finance niche visual elements
    FINANCE_VISUAL_ELEMENTS = {
        "money_saving": "piggy bank, growing stacks of coins, savings jar, budget spreadsheet",
        "passive_income": "money tree, multiple income streams visualization, rental property, dividend stocks",
        "investing": "stock market charts, rising graphs, portfolio diversification, compound interest visualization",
        "budgeting": "expense tracking app, categorized spending, 50/30/20 rule visualization",
        "credit_score": "credit report, score gauge moving upward, payment history timeline",
        "debt_payoff": "debt snowball visualization, decreasing debt bars, celebration of milestone",
        "side_hustle": "laptop with earnings dashboard, freelance workspace, online business icons",
        "tax_strategies": "tax forms, deduction checklist, refund visualization"
    }

    def __init__(self, character_style: CharacterStyle = CharacterStyle.NO_FACE):
        """
        Initialize brand character manager.

        Args:
            character_style: Brand character style to use
        """
        self.character_style = character_style
        self.character_data = self.CHARACTER_DESCRIPTIONS.get(character_style, {})

    def get_character_prompt_prefix(self) -> str:
        """
        Get consistent character description to prepend to all video prompts.

        Returns:
            Character description string
        """
        return self.character_data.get("description", "")

    def enhance_prompt_with_character(
        self,
        scene_prompt: str,
        topic_category: Optional[str] = None
    ) -> str:
        """
        Enhance scene prompt with consistent character and visual style.

        Args:
            scene_prompt: Original scene description
            topic_category: Finance topic category (money_saving, investing, etc.)

        Returns:
            Enhanced prompt with character consistency
        """
        # Start with character description
        enhanced_prompt = self.character_data.get("description", "")

        # Add camera style
        camera_style = self.character_data.get("camera_style", "")
        if camera_style:
            enhanced_prompt += f" {camera_style}."

        # Add finance visual elements if topic category specified
        if topic_category and topic_category in self.FINANCE_VISUAL_ELEMENTS:
            visual_elements = self.FINANCE_VISUAL_ELEMENTS[topic_category]
            enhanced_prompt += f" Visual elements: {visual_elements}."

        # Add scene-specific content
        enhanced_prompt += f" Scene: {scene_prompt}"

        # Add production quality guidelines with smooth ending
        enhanced_prompt += " Professional production quality, well-lit, sharp focus, cinematic composition. The clip should have a natural, smooth ending that can transition seamlessly to the next scene - avoid abrupt cuts mid-action."

        return enhanced_prompt

    def get_brand_guidelines(self) -> Dict[str, Any]:
        """
        Get complete brand guidelines for video generation.

        Returns:
            Brand guidelines dictionary
        """
        return {
            "character_style": self.character_style.value,
            "visual_style": self.character_data.get("visual_style", ""),
            "description": self.character_data.get("description", ""),
            "camera_style": self.character_data.get("camera_style", ""),
            "suitable_for": self.character_data.get("suitable_for", []),
            "color_scheme": {
                "primary": "#1e3a8a",  # Navy blue
                "secondary": "#d4af37",  # Gold
                "accent": "#ffffff",  # White
                "text": "#1f2937"  # Dark gray
            },
            "typography": {
                "primary_font": "Inter, SF Pro Display",
                "style": "Bold headlines, clean sans-serif body"
            }
        }

    @staticmethod
    def detect_topic_category(script: str) -> str:
        """
        Detect finance topic category from script content.

        Args:
            script: Video script text

        Returns:
            Topic category key
        """
        script_lower = script.lower()

        # Check for keywords in priority order
        if any(word in script_lower for word in ["save", "saving", "budget"]):
            return "money_saving"
        elif any(word in script_lower for word in ["passive income", "side hustle", "extra income"]):
            return "passive_income"
        elif any(word in script_lower for word in ["invest", "stock", "portfolio", "dividend"]):
            return "investing"
        elif any(word in script_lower for word in ["credit score", "credit report", "fico"]):
            return "credit_score"
        elif any(word in script_lower for word in ["debt", "payoff", "loan"]):
            return "debt_payoff"
        elif any(word in script_lower for word in ["tax", "deduction", "refund"]):
            return "tax_strategies"
        else:
            return "money_saving"  # Default

    def create_custom_character(
        self,
        description: str,
        visual_style: str,
        camera_style: str,
        suitable_for: list
    ) -> None:
        """
        Create a custom brand character.

        Args:
            description: Detailed character description
            visual_style: Visual style summary
            camera_style: Camera and framing guidelines
            suitable_for: List of suitable content types
        """
        self.character_style = CharacterStyle.CUSTOM
        self.character_data = {
            "visual_style": visual_style,
            "description": description,
            "camera_style": camera_style,
            "suitable_for": suitable_for
        }


# Convenience functions
def get_no_face_character() -> BrandCharacterManager:
    """Get no-face brand character (recommended for consistency)."""
    return BrandCharacterManager(CharacterStyle.NO_FACE)


def get_professional_male_character() -> BrandCharacterManager:
    """Get professional male finance expert character."""
    return BrandCharacterManager(CharacterStyle.PROFESSIONAL_MALE)


def get_relatable_female_character() -> BrandCharacterManager:
    """Get relatable millennial advisor character."""
    return BrandCharacterManager(CharacterStyle.RELATABLE_FEMALE)
