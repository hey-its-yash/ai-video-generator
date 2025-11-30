"""
Advanced Scene Builder for Semantic Scene Generation
Provides intelligent scene construction with:
- Keyword extraction (nouns, verbs, adjectives)
- Theme and mood detection
- Context-aware visual prompt generation
- Scene continuity and coherence
- Duration estimation based on syllables
- Negative prompts to avoid artifacts
"""
import re
import logging
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# THEME AND MOOD DEFINITIONS
# ============================================================================

class Theme(Enum):
    """Detected themes from poem content"""
    NATURE = "nature"
    CELESTIAL = "celestial"      # stars, moon, sun, sky
    ANIMALS = "animals"
    WEATHER = "weather"          # rain, snow, wind
    TIME_OF_DAY = "time_of_day"  # morning, night, evening
    EMOTIONS = "emotions"
    FANTASY = "fantasy"          # magic, fairy, dragon
    DOMESTIC = "domestic"        # home, family, kitchen
    ADVENTURE = "adventure"
    SEASONS = "seasons"


class Mood(Enum):
    """Emotional mood of the scene"""
    JOYFUL = "joyful"
    PEACEFUL = "peaceful"
    MYSTERIOUS = "mysterious"
    PLAYFUL = "playful"
    SAD = "sad"
    EXCITING = "exciting"
    DREAMY = "dreamy"
    COZY = "cozy"
    MAGICAL = "magical"


# ============================================================================
# KEYWORD DICTIONARIES FOR SEMANTIC ANALYSIS
# ============================================================================

CELESTIAL_KEYWORDS = {
    'star', 'stars', 'moon', 'sun', 'sky', 'heaven', 'heavens',
    'twinkle', 'twinkling', 'shine', 'shining', 'glow', 'glowing',
    'diamond', 'sparkle', 'sparkling', 'bright', 'light', 'night',
    'constellation', 'galaxy', 'cosmos', 'celestial'
}

NATURE_KEYWORDS = {
    'tree', 'trees', 'flower', 'flowers', 'garden', 'forest', 'woods',
    'grass', 'meadow', 'field', 'mountain', 'hill', 'river', 'stream',
    'lake', 'ocean', 'sea', 'beach', 'leaf', 'leaves', 'branch', 'rose',
    'blossom', 'bloom', 'petal', 'seed', 'root', 'bush', 'vine'
}

ANIMAL_KEYWORDS = {
    'bird', 'birds', 'cat', 'cats', 'dog', 'dogs', 'rabbit', 'bunny',
    'sheep', 'lamb', 'cow', 'horse', 'duck', 'spider', 'butterfly',
    'bee', 'fish', 'frog', 'mouse', 'owl', 'crow', 'sparrow', 'dove',
    'lion', 'bear', 'wolf', 'fox', 'deer', 'squirrel', 'ant', 'ladybug'
}

WEATHER_KEYWORDS = {
    'rain', 'raining', 'rainy', 'snow', 'snowing', 'snowy', 'wind',
    'windy', 'storm', 'stormy', 'cloud', 'clouds', 'cloudy', 'thunder',
    'lightning', 'rainbow', 'fog', 'foggy', 'mist', 'misty', 'sunshine',
    'sunny', 'breeze', 'hurricane', 'tornado'
}

TIME_KEYWORDS = {
    'morning': ('morning', 'dawn', 'sunrise', 'early', 'breakfast'),
    'day': ('day', 'noon', 'afternoon', 'midday', 'daytime'),
    'evening': ('evening', 'dusk', 'sunset', 'twilight'),
    'night': ('night', 'midnight', 'bedtime', 'sleep', 'dream', 'dark')
}

EMOTION_KEYWORDS = {
    'happy': ('happy', 'joy', 'joyful', 'glad', 'cheerful', 'merry', 'laugh', 'smile'),
    'sad': ('sad', 'cry', 'crying', 'tears', 'weep', 'sorrow', 'grief'),
    'wonder': ('wonder', 'wondering', 'curious', 'amazed', 'amazement'),
    'love': ('love', 'loving', 'dear', 'sweet', 'heart', 'kiss', 'hug'),
    'fear': ('fear', 'afraid', 'scary', 'scared', 'frightened'),
    'peaceful': ('peace', 'peaceful', 'calm', 'quiet', 'gentle', 'soft', 'serene')
}

ACTION_VERBS = {
    'twinkle', 'twinkling', 'sparkle', 'sparkling', 'shine', 'shining',
    'dance', 'dancing', 'jump', 'jumping', 'run', 'running', 'walk', 'walking',
    'fly', 'flying', 'float', 'floating', 'swim', 'swimming', 'hop', 'hopping',
    'skip', 'skipping', 'spin', 'spinning', 'swing', 'swinging', 'wave', 'waving',
    'fall', 'falling', 'rise', 'rising', 'climb', 'climbing', 'hide', 'hiding',
    'play', 'playing', 'sing', 'singing', 'laugh', 'laughing', 'cry', 'crying',
    'sleep', 'sleeping', 'wake', 'waking', 'dream', 'dreaming', 'wonder', 'wondering',
    'sit', 'sitting', 'stand', 'standing', 'roll', 'rolling', 'bounce', 'bouncing'
}

COLOR_WORDS = {
    'red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'white',
    'black', 'gold', 'golden', 'silver', 'gray', 'grey', 'brown', 'violet',
    'scarlet', 'crimson', 'azure', 'navy', 'emerald', 'ruby', 'sapphire'
}


# ============================================================================
# VISUAL MAPPING DICTIONARIES
# ============================================================================

SUBJECT_VISUAL_MAP = {
    # Celestial
    'star': 'a bright glowing star with soft twinkling rays',
    'stars': 'multiple twinkling stars scattered across the sky',
    'moon': 'a luminous crescent moon with a gentle glow',
    'sun': 'a warm radiant sun with golden rays',
    'sky': 'a vast expansive sky with beautiful gradient colors',
    'diamond': 'a brilliant sparkling diamond with prismatic light',
    
    # Nature
    'tree': 'a majestic tree with lush green leaves',
    'flower': 'a delicate flower with soft colorful petals',
    'forest': 'a enchanted forest with towering trees',
    'garden': 'a beautiful garden with colorful blooms',
    'river': 'a peaceful flowing river with crystal clear water',
    'mountain': 'a majestic snow-capped mountain',
    
    # Animals
    'bird': 'a cheerful bird with colorful feathers',
    'cat': 'a fluffy adorable cat with bright eyes',
    'dog': 'a friendly playful dog with wagging tail',
    'rabbit': 'a soft fluffy rabbit with long ears',
    'butterfly': 'a beautiful butterfly with vibrant wings',
    'spider': 'a small spider spinning a delicate web',
    'sheep': 'a fluffy woolly sheep in a green meadow',
    'lamb': 'a cute little lamb with soft wool',
    'cow': 'a friendly spotted cow in a pasture',
    'horse': 'a majestic horse with flowing mane',
    'duck': 'a cheerful duck waddling happily',
    'pig': 'a pink piglet playing in the mud',
    'chicken': 'a plump hen pecking at the ground',
    'goat': 'a playful goat with small horns',
    
    # Characters
    'boy': 'a cheerful young boy with bright curious eyes',
    'girl': 'a sweet young girl with a warm smile',
    'baby': 'an adorable baby with rosy cheeks',
    'mother': 'a loving mother with gentle expression',
    'father': 'a caring father with warm smile',
    'child': 'a happy child with wonder in their eyes',
    'children': 'joyful children playing together',
}

SETTING_VISUAL_MAP = {
    'night': 'deep blue night sky filled with twinkling stars',
    'morning': 'soft golden morning light with dew drops',
    'evening': 'warm orange and pink sunset colors',
    'day': 'bright cheerful daylight with blue sky',
    'rain': 'gentle rain falling with puddle reflections',
    'snow': 'soft white snow covering everything peacefully',
    'spring': 'blooming flowers and fresh green leaves',
    'summer': 'bright sunny day with lush greenery',
    'autumn': 'warm colored falling leaves in orange and gold',
    'winter': 'peaceful snowy landscape with bare trees',
}

MOOD_VISUAL_MAP = {
    Mood.JOYFUL: 'bright vibrant colors, warm lighting, happy atmosphere',
    Mood.PEACEFUL: 'soft pastel colors, gentle lighting, serene calm atmosphere',
    Mood.MYSTERIOUS: 'deep blues and purples, soft glowing lights, enchanting atmosphere',
    Mood.PLAYFUL: 'bright primary colors, dynamic composition, fun energetic feel',
    Mood.SAD: 'muted cool colors, soft diffused light, gentle melancholic mood',
    Mood.EXCITING: 'vivid saturated colors, dramatic lighting, dynamic action',
    Mood.DREAMY: 'soft ethereal colors, glowing light, magical dreamy atmosphere',
    Mood.COZY: 'warm golden tones, soft indoor lighting, comfortable inviting feel',
    Mood.MAGICAL: 'sparkles and glowing particles, enchanted lighting, fantasy atmosphere',
}

CAMERA_MOVEMENTS = {
    'action': 'dynamic camera following the action',
    'reveal': 'slow dramatic reveal with camera pan',
    'focus': 'gentle zoom to focal point',
    'wide': 'establishing wide shot showing full scene',
    'close': 'intimate close-up on subject',
    'floating': 'dreamy floating camera movement',
    'ascending': 'upward camera movement toward the sky',
    'descending': 'downward gentle camera descent',
}


# ============================================================================
# DATA CLASSES FOR SCENE ANALYSIS
# ============================================================================

@dataclass
class ExtractedKeywords:
    """Extracted keywords from text"""
    nouns: List[str] = field(default_factory=list)
    verbs: List[str] = field(default_factory=list)
    adjectives: List[str] = field(default_factory=list)
    subjects: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    colors: List[str] = field(default_factory=list)
    all_keywords: List[str] = field(default_factory=list)


@dataclass
class ThemeAnalysis:
    """Theme and mood analysis result"""
    primary_theme: Theme
    secondary_themes: List[Theme]
    mood: Mood
    time_of_day: str
    setting_elements: List[str]
    emotional_tone: str


@dataclass
class RefinedScene:
    """A refined scene with enhanced prompt"""
    scene_number: int
    text_line: str
    refined_prompt: str
    negative_prompt: str
    duration: float
    transition: str
    keywords: List[str]
    mood: str
    camera_movement: str
    continuity_elements: Dict[str, Any]


# ============================================================================
# SCENE BUILDER CLASS
# ============================================================================

class SceneBuilder:
    """
    Advanced Scene Builder for creating semantically accurate scene prompts
    from poem/rhyme text lines.
    """
    
    def __init__(self, style: str = "children_book"):
        self.style = style
        self.style_suffix = self._get_style_suffix(style)
        self.previous_scene_elements = {}  # For continuity tracking
        
    def _get_style_suffix(self, style: str) -> str:
        """Get style-specific visual suffix"""
        style_map = {
            "children_book": "colorful children's book illustration style, cute whimsical characters, soft rounded shapes, warm inviting colors, storybook aesthetic",
            "cartoon": "bright cartoon animation style, bold outlines, exaggerated expressions, saturated colors, playful animated look",
            "watercolor": "soft watercolor painting style, gentle brushstrokes, dreamy pastel colors, artistic hand-painted aesthetic",
            "3d": "high-quality 3D rendered style, Pixar-like quality, smooth professional CGI, vibrant lighting",
            "anime": "beautiful anime art style, expressive eyes, detailed linework, vibrant colors, Japanese animation aesthetic",
            "realistic": "photorealistic style, cinematic quality, detailed textures, natural lighting",
        }
        return style_map.get(style, style_map["children_book"])
    
    # ========================================================================
    # KEYWORD EXTRACTION
    # ========================================================================
    
    def extract_keywords(self, text: str) -> ExtractedKeywords:
        """
        Extract meaningful keywords from text including nouns, verbs, 
        adjectives, and semantic categories.
        
        Args:
            text: The poem line or text to analyze
            
        Returns:
            ExtractedKeywords with categorized words
        """
        text_lower = text.lower()
        words = re.findall(r'\b[a-zA-Z]+\b', text_lower)
        
        result = ExtractedKeywords()
        
        # FIRST: Extract color + noun phrases (e.g., "black sheep", "little star")
        # This captures important descriptive combinations
        color_noun_patterns = [
            (r'\b(black|white|red|blue|green|yellow|brown|golden|silver|pink|purple)\s+(sheep|cat|dog|bird|horse|cow|star|moon|sun|rabbit|duck|pig|bear|wolf|fox)\b', 'colored_subject'),
            (r'\b(little|big|tiny|huge|small|large)\s+(star|boy|girl|lamb|bird|cat|dog|sheep)\b', 'sized_subject'),
        ]
        
        for pattern, ptype in color_noun_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if ptype == 'colored_subject':
                    color, subject = match
                    result.colors.append(color)
                    result.subjects.append(f"{color} {subject}")  # Keep the full phrase
                    result.adjectives.append(color)
                elif ptype == 'sized_subject':
                    size, subject = match
                    result.subjects.append(f"{size} {subject}")
                    result.adjectives.append(size)
        
        for word in words:
            # Check subjects (nouns representing main entities)
            if word in SUBJECT_VISUAL_MAP or word in ANIMAL_KEYWORDS or word in CELESTIAL_KEYWORDS:
                # Only add if not already captured as part of a phrase
                if not any(word in s for s in result.subjects):
                    result.subjects.append(word)
                result.nouns.append(word)
            
            # Check nature elements
            if word in NATURE_KEYWORDS:
                result.nouns.append(word)
            
            # Check action verbs
            if word in ACTION_VERBS:
                result.verbs.append(word)
                result.actions.append(word)
            
            # Check colors (if not already added from phrases)
            if word in COLOR_WORDS and word not in result.colors:
                result.colors.append(word)
                result.adjectives.append(word)
            
            # Check weather
            if word in WEATHER_KEYWORDS:
                result.nouns.append(word)
        
        # Build all keywords list (deduplicated)
        all_kw = set(result.nouns + result.verbs + result.adjectives + result.subjects)
        result.all_keywords = list(all_kw)
        
        return result
    
    # ========================================================================
    # THEME DETECTION
    # ========================================================================
    
    def detect_theme(self, text: str) -> ThemeAnalysis:
        """
        Detect the primary theme, mood, and context from poem text.
        
        Args:
            text: The poem text to analyze
            
        Returns:
            ThemeAnalysis with detected themes and mood
        """
        text_lower = text.lower()
        words = set(re.findall(r'\b[a-zA-Z]+\b', text_lower))
        
        # Detect primary theme based on keyword overlap
        theme_scores = {
            Theme.CELESTIAL: len(words & CELESTIAL_KEYWORDS),
            Theme.NATURE: len(words & NATURE_KEYWORDS),
            Theme.ANIMALS: len(words & ANIMAL_KEYWORDS),
            Theme.WEATHER: len(words & WEATHER_KEYWORDS),
        }
        
        # Sort themes by score
        sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
        primary_theme = sorted_themes[0][0] if sorted_themes[0][1] > 0 else Theme.NATURE
        secondary_themes = [t for t, s in sorted_themes[1:3] if s > 0]
        
        # Detect time of day - PRIORITY ORDER:
        # 1. If celestial (stars, moon, night sky) -> night
        # 2. Explicit time keywords
        # 3. Default to day
        time_of_day = "day"  # Default
        
        # Check for celestial elements that imply night
        celestial_night_words = {'star', 'stars', 'moon', 'twinkle', 'twinkling', 
                                  'night', 'dark', 'midnight', 'diamond'}
        if words & celestial_night_words:
            time_of_day = "night"
        else:
            # Check explicit time keywords
            for tod, keywords in TIME_KEYWORDS.items():
                if any(kw in text_lower for kw in keywords):
                    time_of_day = tod
                    break
        
        # Detect mood
        mood = Mood.PEACEFUL  # Default
        for mood_type, keywords in EMOTION_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                if mood_type == 'happy':
                    mood = Mood.JOYFUL
                elif mood_type == 'sad':
                    mood = Mood.SAD
                elif mood_type == 'wonder':
                    mood = Mood.MAGICAL
                elif mood_type == 'peaceful':
                    mood = Mood.PEACEFUL
                break
        
        # Check for magical/fantasy elements
        if any(word in text_lower for word in ['magic', 'fairy', 'dream', 'wonder', 'diamond', 'sparkle', 'twinkle']):
            mood = Mood.MAGICAL
        
        # Collect setting elements based on time of day
        setting_elements = []
        if time_of_day in SETTING_VISUAL_MAP:
            setting_elements.append(SETTING_VISUAL_MAP[time_of_day])
        
        # Determine emotional tone
        emotional_tone = "warm and gentle" if mood in [Mood.PEACEFUL, Mood.COZY, Mood.DREAMY] else "bright and cheerful"
        
        return ThemeAnalysis(
            primary_theme=primary_theme,
            secondary_themes=secondary_themes,
            mood=mood,
            time_of_day=time_of_day,
            setting_elements=setting_elements,
            emotional_tone=emotional_tone
        )
    
    # ========================================================================
    # DURATION ESTIMATION
    # ========================================================================
    
    def estimate_duration(self, text: str, base_duration: float = 5.0) -> float:
        """
        Estimate scene duration based on syllable count and rhythm.
        
        Args:
            text: The narration text
            base_duration: Base duration in seconds
            
        Returns:
            Estimated duration in seconds
        """
        # Count syllables (approximation based on vowel groups)
        vowels = 'aeiouy'
        words = text.lower().split()
        syllable_count = 0
        
        for word in words:
            word = word.strip('.,!?;:\'"')
            if not word:
                continue
                
            # Count vowel groups
            count = 0
            prev_was_vowel = False
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not prev_was_vowel:
                    count += 1
                prev_was_vowel = is_vowel
            
            # Minimum 1 syllable per word
            syllable_count += max(1, count)
        
        # Average speaking rate: ~3-4 syllables per second for children's narration
        # We use 3 syllables/second for slower, clearer narration
        speaking_rate = 3.0
        estimated_duration = syllable_count / speaking_rate
        
        # Add small buffer for pauses
        estimated_duration += 0.5
        
        # Clamp between reasonable bounds
        return max(3.0, min(8.0, estimated_duration))
    
    # ========================================================================
    # PROMPT GENERATION
    # ========================================================================
    
    def make_scene_prompt(
        self,
        text_line: str,
        scene_number: int,
        total_scenes: int,
        theme_analysis: Optional[ThemeAnalysis] = None,
        keywords: Optional[ExtractedKeywords] = None
    ) -> str:
        """
        Create a detailed, semantically accurate scene prompt.
        
        Args:
            text_line: The poem line for this scene
            scene_number: Current scene number
            total_scenes: Total number of scenes
            theme_analysis: Pre-analyzed theme (optional)
            keywords: Pre-extracted keywords (optional)
            
        Returns:
            Refined prompt string for video generation
        """
        # Extract keywords if not provided
        if keywords is None:
            keywords = self.extract_keywords(text_line)
        
        # Detect theme if not provided
        if theme_analysis is None:
            theme_analysis = self.detect_theme(text_line)
        
        prompt_parts = []
        
        # 1. SUBJECT - What is the main focus?
        # Handle colored/modified subjects like "black sheep" specially
        subjects_description = []
        for subject in keywords.subjects[:3]:  # Limit to top 3 subjects
            # Check if it's a color+noun phrase (e.g., "black sheep")
            if ' ' in subject:
                # It's a phrase like "black sheep" or "little star"
                parts = subject.split()
                if len(parts) == 2:
                    modifier, noun = parts
                    if noun in SUBJECT_VISUAL_MAP:
                        # Get base description and inject the modifier
                        base_desc = SUBJECT_VISUAL_MAP[noun]
                        # Replace generic article with the modifier
                        if base_desc.startswith('a '):
                            modified_desc = f"a {modifier} " + base_desc[2:]
                        elif base_desc.startswith('an '):
                            modified_desc = f"a {modifier} " + base_desc[3:]
                        else:
                            modified_desc = f"{modifier} {base_desc}"
                        subjects_description.append(modified_desc)
                    else:
                        subjects_description.append(f"a {subject}")
                else:
                    subjects_description.append(f"a {subject}")
            elif subject in SUBJECT_VISUAL_MAP:
                subjects_description.append(SUBJECT_VISUAL_MAP[subject])
            else:
                subjects_description.append(f"a {subject}")
        
        if subjects_description:
            prompt_parts.append(", ".join(subjects_description))
        else:
            # Fallback to describing the line content
            prompt_parts.append(f"a scene depicting: {text_line}")
        
        # 2. ACTION - What is happening?
        if keywords.actions:
            action_text = ", ".join(keywords.actions[:2])
            prompt_parts.append(f"{action_text} gracefully")
        
        # 3. SETTING - Where is it happening?
        if theme_analysis.setting_elements:
            prompt_parts.append(f"set against {theme_analysis.setting_elements[0]}")
        else:
            # Infer setting from theme
            if theme_analysis.primary_theme == Theme.CELESTIAL:
                prompt_parts.append("in the vast night sky filled with stars")
            elif theme_analysis.primary_theme == Theme.NATURE:
                prompt_parts.append("in a beautiful natural landscape")
            elif theme_analysis.primary_theme == Theme.WEATHER:
                prompt_parts.append("with atmospheric weather effects")
        
        # 4. MOOD - How does it feel?
        mood_visual = MOOD_VISUAL_MAP.get(theme_analysis.mood, MOOD_VISUAL_MAP[Mood.MAGICAL])
        prompt_parts.append(mood_visual)
        
        # 5. COLORS - Specific color palette
        if keywords.colors:
            color_text = ", ".join(keywords.colors)
            prompt_parts.append(f"featuring {color_text} tones")
        
        # 6. STYLE - Consistent visual style
        prompt_parts.append(self.style_suffix)
        
        # 7. CAMERA MOVEMENT - Dynamic cinematography
        if scene_number == 1:
            camera = CAMERA_MOVEMENTS['wide']
        elif scene_number == total_scenes:
            camera = CAMERA_MOVEMENTS['ascending']
        elif keywords.actions:
            camera = CAMERA_MOVEMENTS['action']
        else:
            camera = CAMERA_MOVEMENTS['floating']
        prompt_parts.append(camera)
        
        # 8. QUALITY MODIFIERS
        prompt_parts.append("professional quality, cinematic lighting, highly detailed")
        
        # Combine all parts
        refined_prompt = ". ".join(prompt_parts)
        
        return refined_prompt
    
    def make_negative_prompt(self, theme_analysis: ThemeAnalysis) -> str:
        """
        Generate negative prompt to avoid unwanted artifacts.
        
        Args:
            theme_analysis: The theme analysis for context
            
        Returns:
            Negative prompt string
        """
        base_negatives = [
            "text", "watermark", "logo", "signature", "words", "letters",
            "blurry", "low quality", "distorted", "deformed",
            "ugly", "scary", "violent", "dark themes",
            "realistic human faces", "photorealistic faces",
            "modern technology", "phones", "computers", "cars",
            "buildings", "skyscrapers", "urban", "city",
            "inappropriate content", "adult content",
        ]
        
        # Add theme-specific negatives
        if theme_analysis.primary_theme == Theme.CELESTIAL:
            base_negatives.extend(["indoor scene", "daytime unless specified"])
        elif theme_analysis.time_of_day == "night":
            base_negatives.extend(["bright daylight", "sunny"])
        
        return "Negative: " + ", ".join(base_negatives)
    
    # ========================================================================
    # CONTINUITY MANAGEMENT
    # ========================================================================
    
    def apply_continuity(
        self,
        current_scene: Dict[str, Any],
        previous_elements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply visual continuity from previous scene.
        
        Args:
            current_scene: Current scene data
            previous_elements: Elements from previous scene to maintain
            
        Returns:
            Updated scene data with continuity applied
        """
        continuity_elements = {}
        
        # Maintain consistent elements
        if 'sky_color' in previous_elements:
            continuity_elements['sky_color'] = previous_elements['sky_color']
        if 'time_of_day' in previous_elements:
            continuity_elements['time_of_day'] = previous_elements['time_of_day']
        if 'style' in previous_elements:
            continuity_elements['style'] = previous_elements['style']
        if 'color_palette' in previous_elements:
            continuity_elements['color_palette'] = previous_elements['color_palette']
        
        # Store current scene's key elements for next scene
        current_scene['continuity_elements'] = continuity_elements
        
        # Add continuity note to prompt if exists
        if continuity_elements:
            continuity_note = "Maintaining visual continuity with "
            if 'sky_color' in continuity_elements:
                continuity_note += f"{continuity_elements['sky_color']} sky, "
            if 'time_of_day' in continuity_elements:
                continuity_note += f"{continuity_elements['time_of_day']} lighting, "
            current_scene['continuity_note'] = continuity_note.rstrip(", ")
        
        return current_scene
    
    def get_transition(self, scene_number: int, total_scenes: int, mood: Mood) -> str:
        """
        Determine appropriate transition type for scene.
        
        Args:
            scene_number: Current scene number
            total_scenes: Total scenes
            mood: Scene mood
            
        Returns:
            Transition type string
        """
        if scene_number == 1:
            return "fade_in"
        elif scene_number == total_scenes:
            return "fade_out"
        elif mood in [Mood.PEACEFUL, Mood.DREAMY]:
            return "crossfade"
        elif mood in [Mood.EXCITING, Mood.PLAYFUL]:
            return "swipe"
        else:
            return "crossfade"
    
    # ========================================================================
    # MAIN BUILDER METHOD
    # ========================================================================
    
    def build_refined_scenes(
        self,
        poem_lines: List[str],
        num_scenes: int
    ) -> List[RefinedScene]:
        """
        Build refined scenes from poem lines with full semantic analysis.
        
        Args:
            poem_lines: List of poem lines
            num_scenes: Number of scenes to generate
            
        Returns:
            List of RefinedScene objects
        """
        refined_scenes = []
        
        # Analyze full poem for overall theme - THIS SETS GLOBAL CONTEXT
        full_poem = " ".join(poem_lines)
        overall_theme = self.detect_theme(full_poem)
        
        logger.info(f"Overall poem theme: {overall_theme.primary_theme.value}, "
                   f"Time: {overall_theme.time_of_day}, Mood: {overall_theme.mood.value}")
        
        # Distribute lines to scenes
        lines_per_scene = max(1, len(poem_lines) // num_scenes)
        
        previous_elements = {
            'time_of_day': overall_theme.time_of_day,
            'style': self.style,
            'sky_color': 'deep blue' if overall_theme.time_of_day == 'night' else 'bright blue',
            'mood': overall_theme.mood
        }
        
        for i in range(num_scenes):
            # Get lines for this scene
            start_idx = i * lines_per_scene
            end_idx = start_idx + lines_per_scene if i < num_scenes - 1 else len(poem_lines)
            scene_lines = poem_lines[start_idx:end_idx] if start_idx < len(poem_lines) else [poem_lines[-1]]
            scene_text = " ".join(scene_lines)
            
            # Extract keywords for this specific scene
            keywords = self.extract_keywords(scene_text)
            
            # Detect theme for this scene BUT inherit time_of_day from overall poem
            theme = self.detect_theme(scene_text)
            
            # CRITICAL: Use overall poem's time_of_day for VISUAL CONTINUITY
            # Individual lines may not have celestial words but the poem context does
            theme.time_of_day = overall_theme.time_of_day
            
            # Update setting elements to match overall context
            if theme.time_of_day in SETTING_VISUAL_MAP:
                theme.setting_elements = [SETTING_VISUAL_MAP[theme.time_of_day]]
            
            # Generate refined prompt with consistent context
            refined_prompt = self.make_scene_prompt(
                text_line=scene_text,
                scene_number=i + 1,
                total_scenes=num_scenes,
                theme_analysis=theme,
                keywords=keywords
            )
            
            # Generate negative prompt with correct time context
            negative_prompt = self.make_negative_prompt(theme)
            
            # Estimate duration
            duration = self.estimate_duration(scene_text)
            
            # Determine transition
            transition = self.get_transition(i + 1, num_scenes, theme.mood)
            
            # Get camera movement
            if keywords.actions:
                camera = "dynamic tracking shot following the action"
            elif i == 0:
                camera = "slow establishing wide shot"
            elif i == num_scenes - 1:
                camera = "gentle upward pan to sky"
            else:
                camera = "smooth floating camera movement"
            
            # Build refined scene
            refined_scene = RefinedScene(
                scene_number=i + 1,
                text_line=scene_text,
                refined_prompt=f"{refined_prompt}. {negative_prompt}",
                negative_prompt=negative_prompt,
                duration=duration,
                transition=transition,
                keywords=keywords.all_keywords,
                mood=theme.mood.value,
                camera_movement=camera,
                continuity_elements=previous_elements.copy()
            )
            
            refined_scenes.append(refined_scene)
            
            # Update continuity elements for next scene
            previous_elements['time_of_day'] = theme.time_of_day
            if keywords.colors:
                previous_elements['color_palette'] = keywords.colors
        
        logger.info(f"Built {len(refined_scenes)} refined scenes with semantic analysis")
        
        return refined_scenes


# ============================================================================
# INTEGRATION HELPERS
# ============================================================================

def create_scene_from_refined(refined: RefinedScene) -> Dict[str, Any]:
    """
    Convert RefinedScene to Scene-compatible dictionary.
    
    Args:
        refined: RefinedScene object
        
    Returns:
        Dictionary compatible with Scene model
    """
    return {
        'scene_number': refined.scene_number,
        'description': refined.refined_prompt,
        'narration': refined.text_line,
        'duration': refined.duration,
        'keywords': refined.keywords,
    }


def build_scenes_from_poem(
    poem_text: str,
    num_scenes: int = 4,
    style: str = "children_book"
) -> List[Dict[str, Any]]:
    """
    Convenience function to build refined scenes from poem text.
    
    Args:
        poem_text: The complete poem text
        num_scenes: Number of scenes to generate
        style: Visual style preset
        
    Returns:
        List of scene dictionaries
    """
    # Split poem into lines
    lines = [line.strip() for line in poem_text.split('\n') if line.strip()]
    
    # Build refined scenes
    builder = SceneBuilder(style=style)
    refined_scenes = builder.build_refined_scenes(lines, num_scenes)
    
    # Convert to scene dictionaries
    scenes = [create_scene_from_refined(r) for r in refined_scenes]
    
    return scenes


# ============================================================================
# TEST / EXAMPLE
# ============================================================================

if __name__ == "__main__":
    # Test with Twinkle Twinkle
    test_poem = """Twinkle, twinkle, little star,
How I wonder what you are.
Up above the world so high,
Like a diamond in the sky."""
    
    print("=" * 70)
    print("SCENE BUILDER TEST")
    print("=" * 70)
    print(f"\nPoem:\n{test_poem}\n")
    
    builder = SceneBuilder(style="children_book")
    lines = [l.strip() for l in test_poem.split('\n') if l.strip()]
    refined_scenes = builder.build_refined_scenes(lines, num_scenes=4)
    
    for scene in refined_scenes:
        print(f"\n{'='*70}")
        print(f"SCENE {scene.scene_number}")
        print(f"{'='*70}")
        print(f"Text Line: {scene.text_line}")
        print(f"\nRefined Prompt:\n{scene.refined_prompt}")
        print(f"\nDuration: {scene.duration:.1f}s")
        print(f"Transition: {scene.transition}")
        print(f"Mood: {scene.mood}")
        print(f"Camera: {scene.camera_movement}")
        print(f"Keywords: {', '.join(scene.keywords)}")
