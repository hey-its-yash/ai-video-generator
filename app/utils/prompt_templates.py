"""
Prompt Templates for LLM Scene Generation
Carefully crafted prompts for converting rhymes into visual scenes
"""

SCENE_GENERATION_SYSTEM_PROMPT = """You are a creative director specializing in children's content. Your task is to convert nursery rhymes and children's stories into vivid, visual scenes perfect for video generation.

Key Requirements:
1. Create child-friendly, colorful, and engaging visual descriptions
2. Maintain consistent style and characters across all scenes
3. Each scene should be visually distinct and interesting
4. Focus on clear, specific visual elements that can be illustrated
5. Include motion and action words for animation
6. Keep narration aligned with the rhyme text
7. Output MUST be valid JSON format
8. Ensure descriptions are safe and appropriate for all ages

Style Guidelines:
- Bright, vibrant colors
- Cute, friendly character designs
- Safe, happy environments
- Clear, simple compositions
- Magical, whimsical atmosphere"""


SCENE_GENERATION_USER_PROMPT = """Convert the following children's rhyme into {num_scenes} visual scenes for a video.

Rhyme:
{rhyme_text}

Style: {style_description}

CRITICAL REQUIREMENTS FOR SEMANTIC ACCURACY:
1. Each scene MUST accurately represent the MEANING of the poem line
2. If the poem mentions "star" - show a star. If it mentions "sky" - show sky.
3. Extract the SUBJECT (star, moon, child, animal), ACTION (twinkle, jump, fly), and SETTING (night, garden, room)
4. Include specific visual elements: colors, lighting, camera angle, mood
5. Add motion/action words for animation (sparkling, floating, dancing)
6. Each scene should be 4-7 seconds based on narration length
7. Maintain visual CONTINUITY across scenes (same sky color, lighting style)

PROMPT STRUCTURE (follow this for each scene description):
- SUBJECT: [What/who is the main focus]
- ACTION: [What is happening]
- SETTING: [Where - time of day, location, atmosphere]
- STYLE: [Visual style - colorful, dreamy, whimsical]
- MOOD: [Emotional tone - peaceful, joyful, magical]
- CAMERA: [Movement - slow pan up, zoom in, floating]
- NEGATIVE: [What to avoid - no text, no modern elements]

Output Format (JSON):
{{
  "title": "Title of the rhyme",
  "style": "Overall visual style description",
  "total_duration": 30,
  "scenes": [
    {{
      "scene_number": 1,
      "description": "A [SUBJECT] [ACTION] in [SETTING]. [STYLE]. [MOOD]. [CAMERA]. Negative: no text, no logos, no modern elements.",
      "narration": "Text to be spoken (exact rhyme text)",
      "duration": 5,
      "keywords": ["subject", "action", "setting", "mood"]
    }}
  ]
}}

EXAMPLE for "Twinkle, twinkle, little star":
{{
  "scene_number": 1,
  "description": "A tiny glowing star twinkles softly with gentle sparkles in the deep blue night sky, surrounded by smaller distant stars and wispy clouds. Soft dreamy watercolor style with warm golden glow. Magical peaceful atmosphere. Slow upward camera pan. Negative: no text, no logos, no buildings, no modern elements.",
  "narration": "Twinkle, twinkle, little star",
  "duration": 4.5,
  "keywords": ["star", "twinkling", "night sky", "magical", "glowing"]
}}

Generate exactly {num_scenes} scenes with ACCURATE semantic representation!"""


STYLE_DESCRIPTIONS = {
    "children_book": """children's book illustration style, colorful and vibrant, whimsical and playful, soft edges, friendly characters, bright lighting, professional children's book art, storybook aesthetic, warm and inviting""",
    
    "cartoon": """cartoon style, animated look, bold outlines, exaggerated features, bright saturated colors, playful composition, TV animation quality, expressive characters, fun and energetic""",
    
    "watercolor": """watercolor painting style, soft dreamy colors, artistic brushstrokes, gentle and peaceful, pastel tones, flowing organic shapes, ethereal atmosphere, hand-painted aesthetic, delicate details""",
    
    "3d": """3D rendered style, Pixar-like quality, smooth professional rendering, cute character design, vibrant lighting, polished and clean, modern CGI animation, rounded friendly shapes, high production value""",
    
    "anime": """anime art style, manga-inspired, expressive large eyes, detailed linework, vibrant colors, dynamic composition, Japanese animation aesthetic, cute chibi proportions, sparkles and effects""",
}


IMAGE_GENERATION_PROMPT_TEMPLATE = """{scene_description}

Style: {style}
Keywords: {keywords}

Additional requirements:
- High quality, professional illustration
- Clear focal point
- Suitable for children
- Bright and colorful
- Well-composed scene
- {resolution} resolution"""


MOTION_PROMPT_TEMPLATE = """Scene: {scene_description}

Action: {narration}

Generate smooth, gentle animation showing: {motion_keywords}

The animation should be:
- Smooth and fluid
- Child-friendly
- Magical and whimsical
- Natural movement
- 5 seconds duration"""


SCENE_REFINEMENT_PROMPT = """The generated scenes need improvement. Please refine them to be more:
1. Visually detailed and specific
2. Consistent in style and characters
3. Engaging and dynamic
4. Suitable for children

Original scenes:
{original_scenes}

Rhyme: {rhyme_text}

Please regenerate the scenes with better visual descriptions and consistency."""


FALLBACK_SCENES_TEMPLATE = """{{
  "title": "{title}",
  "style": "children's book illustration, colorful, vibrant, whimsical",
  "total_duration": {total_duration},
  "scenes": [
    {{
      "scene_number": 1,
      "description": "Opening scene introducing the main character or setting in a bright, colorful children's book style",
      "narration": "First line of the rhyme",
      "duration": 5,
      "keywords": ["colorful", "bright", "cheerful"]
    }}
  ]
}}"""


# Enhanced prompt for video generation with semantic details
ENHANCED_VIDEO_PROMPT_TEMPLATE = """{subject_description}. {action_description}. Set in {setting_description}. 
{mood_description}. {style_suffix}. {camera_movement}. 
Professional quality, highly detailed, cinematic lighting.
Negative: {negative_prompt}"""


def get_enhanced_scene_prompt(
    scene_description: str,
    narration: str,
    style: str = "children_book",
    keywords: list = None,
) -> str:
    """
    Generate an enhanced video prompt with semantic details.
    
    Args:
        scene_description: Base scene description
        narration: The narration text (for context)
        style: Visual style
        keywords: Scene keywords
        
    Returns:
        Enhanced prompt for video generation
    """
    style_suffix = STYLE_DESCRIPTIONS.get(style, STYLE_DESCRIPTIONS["children_book"])
    
    # Build enhanced prompt
    prompt_parts = [scene_description]
    
    # Add style
    prompt_parts.append(style_suffix)
    
    # Add motion/animation cues
    motion_keywords = extract_motion_keywords(scene_description)
    if motion_keywords:
        prompt_parts.append(f"Featuring {', '.join(motion_keywords[:3])} motion")
    
    # Add quality modifiers
    prompt_parts.append("Professional animation quality, smooth movement, cinematic lighting")
    
    # Add negative prompt
    negative = "no text, no watermarks, no logos, no modern elements, no distortion"
    prompt_parts.append(f"Negative: {negative}")
    
    return ". ".join(prompt_parts)


def get_scene_generation_prompt(
    rhyme_text: str,
    num_scenes: int = 6,
    style: str = "children_book",
) -> tuple[str, str]:
    """
    Get the complete prompt for scene generation
    
    Args:
        rhyme_text: The rhyme/story text
        num_scenes: Number of scenes to generate
        style: Visual style preset
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    style_description = STYLE_DESCRIPTIONS.get(style, STYLE_DESCRIPTIONS["children_book"])
    
    user_prompt = SCENE_GENERATION_USER_PROMPT.format(
        rhyme_text=rhyme_text,
        num_scenes=num_scenes,
        style_description=style_description,
    )
    
    return SCENE_GENERATION_SYSTEM_PROMPT, user_prompt


def get_image_generation_prompt(
    scene_description: str,
    style: str = "children_book",
    keywords: list = None,
    resolution: int = 512,
) -> str:
    """
    Get prompt for image generation from scene
    
    Args:
        scene_description: Scene visual description
        style: Visual style
        keywords: Additional keywords
        resolution: Image resolution
        
    Returns:
        Complete image generation prompt
    """
    style_suffix = STYLE_DESCRIPTIONS.get(style, STYLE_DESCRIPTIONS["children_book"])
    keywords_str = ", ".join(keywords) if keywords else "colorful, vibrant, cheerful"
    
    prompt = IMAGE_GENERATION_PROMPT_TEMPLATE.format(
        scene_description=scene_description,
        style=style_suffix,
        keywords=keywords_str,
        resolution=f"{resolution}x{resolution}",
    )
    
    return prompt


def get_motion_prompt(
    scene_description: str,
    narration: str,
    keywords: list = None,
) -> str:
    """
    Get prompt for video motion/animation
    
    Args:
        scene_description: Scene visual description
        narration: Scene narration text
        keywords: Motion keywords
        
    Returns:
        Motion/animation prompt
    """
    motion_keywords = ", ".join(keywords) if keywords else "gentle movement, subtle animation"
    
    prompt = MOTION_PROMPT_TEMPLATE.format(
        scene_description=scene_description,
        narration=narration,
        motion_keywords=motion_keywords,
    )
    
    return prompt


def extract_motion_keywords(description: str) -> list[str]:
    """
    Extract motion-related keywords from description
    
    Args:
        description: Scene description
        
    Returns:
        List of motion keywords
    """
    motion_words = [
        'twinkle', 'twinkling', 'sparkle', 'sparkling', 'glow', 'glowing',
        'dance', 'dancing', 'jump', 'jumping', 'run', 'running',
        'fly', 'flying', 'float', 'floating', 'spin', 'spinning',
        'wave', 'waving', 'sway', 'swaying', 'bounce', 'bouncing',
        'shine', 'shining', 'shimmer', 'shimmering', 'flutter', 'fluttering',
        'move', 'moving', 'rise', 'rising', 'fall', 'falling',
        'swing', 'swinging', 'hop', 'hopping', 'skip', 'skipping',
    ]
    
    description_lower = description.lower()
    found_keywords = [word for word in motion_words if word in description_lower]
    
    # Add generic keywords if none found
    if not found_keywords:
        found_keywords = ['gentle movement', 'subtle animation']
    
    return found_keywords


# Example usage and testing
if __name__ == "__main__":
    # Test prompt generation
    test_rhyme = """Twinkle, twinkle, little star,
How I wonder what you are.
Up above the world so high,
Like a diamond in the sky."""
    
    system_prompt, user_prompt = get_scene_generation_prompt(
        rhyme_text=test_rhyme,
        num_scenes=4,
        style="children_book"
    )
    
    print("=" * 60)
    print("SYSTEM PROMPT:")
    print("=" * 60)
    print(system_prompt)
    print("\n" + "=" * 60)
    print("USER PROMPT:")
    print("=" * 60)
    print(user_prompt)
    print("\n" + "=" * 60)
    
    # Test image prompt
    test_description = "A bright yellow star twinkling in the dark night sky"
    image_prompt = get_image_generation_prompt(
        scene_description=test_description,
        style="children_book",
        keywords=["star", "night", "magical"],
    )
    
    print("IMAGE PROMPT:")
    print("=" * 60)
    print(image_prompt)
    print("\n")
