"""
LLM Service for Scene Generation
Handles conversion of rhymes to visual scenes using multiple LLM providers
Supports: Google Gemini, OpenAI, HuggingFace
"""
import json
import re
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

# LLM clients
import google.generativeai as genai
from openai import AsyncOpenAI
from huggingface_hub import InferenceClient

from app.config import settings
from app.models.schemas import Scene, SceneGenerationResult, LLMProvider
from app.utils.prompt_templates import (
    get_scene_generation_prompt,
    get_enhanced_scene_prompt,
    STYLE_DESCRIPTIONS,
    FALLBACK_SCENES_TEMPLATE,
)
from app.services.scene_builder import SceneBuilder, build_scenes_from_poem

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating scenes from rhymes using LLMs"""
    
    def __init__(self):
        self.gemini_configured = False
        self.openai_configured = False
        self.hf_configured = False
        
        # Initialize Gemini
        if settings.GOOGLE_API_KEY:
            try:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                # Use gemini-2.0-flash which is the stable model
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
                self.gemini_configured = True
                logger.info("✓ Gemini API configured (using gemini-2.0-flash)")
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}")
        
        # Initialize OpenAI
        if settings.OPENAI_API_KEY:
            try:
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                self.openai_configured = True
                logger.info("✓ OpenAI API configured")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")
        
        # Initialize HuggingFace
        if settings.HUGGINGFACE_TOKEN:
            try:
                self.hf_client = InferenceClient(token=settings.HUGGINGFACE_TOKEN)
                self.hf_configured = True
                logger.info("✓ HuggingFace API configured")
            except Exception as e:
                logger.warning(f"HuggingFace initialization failed: {e}")
        
        if not any([self.gemini_configured, self.openai_configured, self.hf_configured]):
            logger.error("No LLM providers configured!")
    
    async def generate_scenes(
        self,
        rhyme_text: str,
        num_scenes: int = 6,
        style: str = "children_book",
        provider: Optional[LLMProvider] = None,
    ) -> SceneGenerationResult:
        """
        Generate visual scenes from rhyme text
        
        Args:
            rhyme_text: The rhyme/story text
            num_scenes: Number of scenes to generate
            style: Visual style preset
            provider: Specific LLM provider to use (None for auto)
            
        Returns:
            SceneGenerationResult with generated scenes
        """
        logger.info(f"Generating {num_scenes} scenes from rhyme")
        logger.info(f"Style: {style}, Provider: {provider or 'auto'}")
        
        # Validate input
        if not rhyme_text or len(rhyme_text.strip()) < 10:
            raise ValueError("Rhyme text is too short")
        
        if num_scenes < 3 or num_scenes > 10:
            raise ValueError("Number of scenes must be between 3 and 10")
        
        # Get prompts
        system_prompt, user_prompt = get_scene_generation_prompt(
            rhyme_text=rhyme_text,
            num_scenes=num_scenes,
            style=style,
        )
        
        # Try providers in order
        providers_to_try = []
        
        if provider:
            # Use specific provider
            providers_to_try.append(provider.value if hasattr(provider, 'value') else provider)
        else:
            # Auto-select based on availability
            if self.gemini_configured:
                providers_to_try.append('gemini')
            if self.openai_configured:
                providers_to_try.append('openai')
            if self.hf_configured:
                providers_to_try.append('huggingface')
        
        last_error = None
        
        for llm_provider in providers_to_try:
            try:
                logger.info(f"Trying provider: {llm_provider}")
                
                if llm_provider == 'gemini':
                    result = await self._generate_with_gemini(system_prompt, user_prompt)
                elif llm_provider == 'openai':
                    result = await self._generate_with_openai(system_prompt, user_prompt)
                elif llm_provider == 'huggingface':
                    result = await self._generate_with_huggingface(system_prompt, user_prompt)
                else:
                    continue
                
                # Parse and validate result
                scenes_data = self._parse_llm_response(result)
                scene_result = self._validate_and_create_scenes(
                    scenes_data, rhyme_text, num_scenes, style
                )
                
                logger.info(f"✓ Successfully generated {len(scene_result.scenes)} scenes using {llm_provider}")
                return scene_result
                
            except Exception as e:
                logger.warning(f"Provider {llm_provider} failed: {e}")
                last_error = e
                continue
        
        # All providers failed, use fallback
        logger.error("All LLM providers failed, using fallback scenes")
        return self._create_fallback_scenes(rhyme_text, num_scenes, style)
    
    async def _generate_with_gemini(self, system_prompt: str, user_prompt: str) -> str:
        """Generate using Google Gemini"""
        if not self.gemini_configured:
            raise ValueError("Gemini not configured")
        
        # Combine prompts
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Configure safety settings to be less restrictive for children's content
        # Note: BLOCK_NONE is required because sometimes innocent children's content 
        # triggers false positives in safety filters.
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]
        
        # Generate
        response = self.gemini_model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=settings.LLM_TEMPERATURE,
                max_output_tokens=settings.MAX_TOKENS,
            ),
            safety_settings=safety_settings,
        )
        
        # Check if response was blocked
        if not response.text:
            if hasattr(response, 'prompt_feedback'):
                raise ValueError(f"Content generation blocked: {response.prompt_feedback}")
            raise ValueError("No text generated from Gemini")
        
        return response.text
    
    async def _generate_with_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Generate using OpenAI"""
        if not self.openai_configured:
            raise ValueError("OpenAI not configured")
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
        )
        
        return response.choices[0].message.content
    
    async def _generate_with_huggingface(self, system_prompt: str, user_prompt: str) -> str:
        """Generate using HuggingFace"""
        if not self.hf_configured:
            raise ValueError("HuggingFace not configured")
        
        # Use a good chat model
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = self.hf_client.text_generation(
            full_prompt,
            model="mistralai/Mistral-7B-Instruct-v0.2",
            max_new_tokens=settings.MAX_TOKENS,
            temperature=settings.LLM_TEMPERATURE,
        )
        
        return response
    
    def _parse_llm_response(self, response: str) -> dict:
        """
        Parse LLM response to extract JSON
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed JSON dict
        """
        # Clean response
        cleaned = response.strip()
        
        # Remove markdown code blocks
        if '```json' in cleaned:
            cleaned = cleaned.split('```json')[1].split('```')[0]
        elif '```' in cleaned:
            # Remove any code block markers
            parts = cleaned.split('```')
            for part in parts:
                if '{' in part and '}' in part:
                    cleaned = part
                    break
        
        cleaned = cleaned.strip()
        
        # Try to find JSON object
        json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            try:
                # Fix common JSON issues
                json_str = json_str.replace('\n', ' ')
                json_str = re.sub(r'\s+', ' ', json_str)
                json_str = json_str.replace('",}', '"}')
                json_str = json_str.replace('",]', '"]')
                
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error: {e}")
                logger.warning(f"Problematic JSON: {json_str[:200]}...")
                pass
        
        # Last resort: try to parse entire response
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            raise ValueError(f"Could not parse JSON from response: {response[:200]}...")
    
    def _validate_and_create_scenes(
        self,
        scenes_data: dict,
        rhyme_text: str,
        expected_scenes: int,
        style: str,
    ) -> SceneGenerationResult:
        """
        Validate and create Scene objects from parsed data
        
        Args:
            scenes_data: Parsed JSON data
            rhyme_text: Original rhyme text
            expected_scenes: Expected number of scenes
            style: Visual style
            
        Returns:
            SceneGenerationResult
        """
        # Extract scenes list
        scenes_list = scenes_data.get('scenes', [])
        
        if not scenes_list:
            raise ValueError("No scenes found in response")
        
        # Ensure we have the right number of scenes
        if len(scenes_list) < expected_scenes:
            logger.warning(f"Got {len(scenes_list)} scenes, expected {expected_scenes}")
        
        # Create Scene objects
        scenes = []
        for i, scene_data in enumerate(scenes_list[:expected_scenes]):
            try:
                scene = Scene(
                    scene_number=scene_data.get('scene_number', i + 1),
                    description=scene_data.get('description', ''),
                    narration=scene_data.get('narration', ''),
                    duration=float(scene_data.get('duration', 5.0)),
                    keywords=scene_data.get('keywords', []),
                )
                scenes.append(scene)
            except Exception as e:
                logger.warning(f"Failed to create scene {i+1}: {e}")
                continue
        
        if not scenes:
            raise ValueError("No valid scenes created")
        
        # Create result
        result = SceneGenerationResult(
            title=scenes_data.get('title', 'Children\'s Rhyme'),
            style=scenes_data.get('style', STYLE_DESCRIPTIONS.get(style, '')),
            scenes=scenes,
            total_duration=sum(s.duration for s in scenes),
        )
        
        return result
    
    def _create_fallback_scenes(
        self,
        rhyme_text: str,
        num_scenes: int,
        style: str,
    ) -> SceneGenerationResult:
        """
        Create semantically-aware fallback scenes when LLM fails.
        Uses SceneBuilder for intelligent scene construction.
        
        Args:
            rhyme_text: Original rhyme
            num_scenes: Number of scenes
            style: Visual style
            
        Returns:
            SceneGenerationResult with refined scenes
        """
        logger.info("Creating enhanced fallback scenes using SceneBuilder")
        
        # Use SceneBuilder for intelligent scene generation
        scene_builder = SceneBuilder(style=style)
        lines = [line.strip() for line in rhyme_text.split('\n') if line.strip()]
        
        # Build refined scenes with semantic analysis
        refined_scenes = scene_builder.build_refined_scenes(lines, num_scenes)
        
        # Convert to Scene objects
        scenes = []
        for refined in refined_scenes:
            scene = Scene(
                scene_number=refined.scene_number,
                description=refined.refined_prompt,
                narration=refined.text_line,
                duration=refined.duration,
                keywords=refined.keywords,
            )
            scenes.append(scene)
        
        # Detect title from content
        overall_theme = scene_builder.detect_theme(rhyme_text)
        title = self._generate_title_from_theme(rhyme_text, overall_theme)
        
        result = SceneGenerationResult(
            title=title,
            style=STYLE_DESCRIPTIONS.get(style, "children's book illustration"),
            scenes=scenes,
            total_duration=sum(s.duration for s in scenes),
        )
        
        logger.info(f"Created {len(scenes)} enhanced scenes with semantic alignment")
        return result
    
    def _generate_title_from_theme(self, text: str, theme_analysis) -> str:
        """Generate a title based on the poem content and theme."""
        # Extract first few significant words
        words = text.split()[:6]
        
        # Common rhyme title patterns
        if 'twinkle' in text.lower():
            return "Twinkle Twinkle Little Star"
        elif 'humpty' in text.lower():
            return "Humpty Dumpty"
        elif 'mary' in text.lower() and 'lamb' in text.lower():
            return "Mary Had a Little Lamb"
        elif 'jack' in text.lower() and 'jill' in text.lower():
            return "Jack and Jill"
        elif 'rain' in text.lower():
            return "Rain Rain Go Away"
        else:
            # Generate from first line
            first_line = text.split('\n')[0].strip()
            return first_line[:40] if len(first_line) > 40 else first_line
    
    def get_available_providers(self) -> List[str]:
        """Get list of configured LLM providers"""
        providers = []
        if self.gemini_configured:
            providers.append('gemini')
        if self.openai_configured:
            providers.append('openai')
        if self.hf_configured:
            providers.append('huggingface')
        return providers


# Global service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


# Convenience function
async def generate_scenes_from_rhyme(
    rhyme_text: str,
    num_scenes: int = 6,
    style: str = "children_book",
    provider: Optional[str] = None,
) -> SceneGenerationResult:
    """
    Generate scenes from rhyme text
    
    Args:
        rhyme_text: The rhyme text
        num_scenes: Number of scenes
        style: Visual style
        provider: LLM provider to use
        
    Returns:
        SceneGenerationResult
    """
    service = get_llm_service()
    return await service.generate_scenes(
        rhyme_text=rhyme_text,
        num_scenes=num_scenes,
        style=style,
        provider=provider,
    )


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        """Test LLM service"""
        service = get_llm_service()
        
        print("Available providers:", service.get_available_providers())
        
        test_rhyme = """Twinkle, twinkle, little star,
How I wonder what you are.
Up above the world so high,
Like a diamond in the sky.
Twinkle, twinkle, little star,
How I wonder what you are."""
        
        print("\nGenerating scenes...")
        result = await service.generate_scenes(
            rhyme_text=test_rhyme,
            num_scenes=6,
            style="children_book",
        )
        
        print(f"\nTitle: {result.title}")
        print(f"Style: {result.style}")
        print(f"Total Duration: {result.total_duration}s")
        print(f"\nScenes:")
        for scene in result.scenes:
            print(f"\n  Scene {scene.scene_number}:")
            print(f"    Description: {scene.description[:100]}...")
            print(f"    Narration: {scene.narration}")
            print(f"    Duration: {scene.duration}s")
            print(f"    Keywords: {', '.join(scene.keywords)}")
    
    asyncio.run(test())
