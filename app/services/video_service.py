"""
Video Generation Service
Handles image-to-video and text-to-video generation
Supports: LTX-Video, Stable Video Diffusion, Google Veo 3.1
"""
import os
import io
import base64
import asyncio
import time
from pathlib import Path
from typing import Optional, Union, Tuple
import logging

from huggingface_hub import InferenceClient
import httpx
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)

# Google Veo support
try:
    from google import genai
    from google.genai import types
    VEO_AVAILABLE = True
except ImportError:
    VEO_AVAILABLE = False
    logger.warning("Google Veo not available. Install with: pip install google-genai")


class VideoGenerationService:
    """Service for generating videos from images or text"""
    
    def __init__(self):
        self.hf_token = settings.HUGGINGFACE_TOKEN
        self.google_api_key = settings.GOOGLE_API_KEY
        
        if not self.hf_token:
            logger.warning("HuggingFace token not configured. Video generation may fail.")
        
        # Initialize InferenceClient with fal-ai provider for LTX-Video
        self.client = InferenceClient(
            provider="fal-ai",
            api_key=self.hf_token,
        )
        
        # Fallback client for other models
        self.fallback_client = InferenceClient(
            token=self.hf_token,
        )
        
        # Initialize Google Veo client
        self.veo_client = None
        if VEO_AVAILABLE and self.google_api_key:
            try:
                self.veo_client = genai.Client(api_key=self.google_api_key)
                logger.info("✓ Google Veo 3.1 client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Veo client: {e}")
    
    async def generate_video_from_image(
        self,
        image_path: Union[str, Path],
        prompt: str,
        model: Optional[str] = None,
        duration: int = 5,
        use_fallback: bool = False,
    ) -> Tuple[bytes, str]:
        """
        Generate video from image using LTX-Video or fallback models
        
        Args:
            image_path: Path to input image
            prompt: Text prompt describing desired motion/action
            model: Model to use (default: from settings)
            duration: Video duration in seconds
            use_fallback: Use fallback model if primary fails
            
        Returns:
            Tuple of (video_bytes, model_used)
        """
        model = model or settings.VIDEO_MODEL
        
        try:
            logger.info(f"Generating video from image using {model}")
            logger.info(f"Prompt: {prompt}")
            
            # Read image file
            with open(image_path, "rb") as f:
                input_image = f.read()
            
            # Try primary model (LTX-Video with fal-ai)
            if "LTX-Video" in model and not use_fallback:
                video_bytes = await self._generate_with_ltx_video(
                    input_image, prompt, duration
                )
                return video_bytes, model
            
            # Try fallback model (Stable Video Diffusion)
            else:
                video_bytes = await self._generate_with_svd(
                    input_image, prompt, duration
                )
                return video_bytes, settings.VIDEO_MODEL_FALLBACK
                
        except Exception as e:
            logger.error(f"Error generating video with {model}: {e}")
            
            # Try fallback if not already using it
            if not use_fallback and settings.VIDEO_MODEL_FALLBACK:
                logger.info(f"Trying fallback model: {settings.VIDEO_MODEL_FALLBACK}")
                return await self.generate_video_from_image(
                    image_path=image_path,
                    prompt=prompt,
                    model=settings.VIDEO_MODEL_FALLBACK,
                    duration=duration,
                    use_fallback=True,
                )
            
            raise
    
    async def _generate_with_ltx_video(
        self,
        image_bytes: bytes,
        prompt: str,
        duration: int = 5,
    ) -> bytes:
        """
        Generate video using Lightricks/LTX-Video via fal-ai
        
        Args:
            image_bytes: Input image as bytes
            prompt: Motion/action prompt
            duration: Video duration
            
        Returns:
            Video bytes
        """
        try:
            # Run in thread pool since InferenceClient is sync
            loop = asyncio.get_event_loop()
            video = await loop.run_in_executor(
                None,
                lambda: self.client.image_to_video(
                    image_bytes,
                    prompt=prompt,
                    model="Lightricks/LTX-Video",
                )
            )
            
            # Handle tuple response (url, other_data)
            if isinstance(video, tuple):
                video = video[0]  # Extract the URL or bytes from tuple
            
            # video is already bytes from the API
            if isinstance(video, bytes):
                return video
            
            # If it's a file-like object, read it
            if hasattr(video, 'read'):
                return video.read()
            
            # If it's a path or URL, fetch it
            if isinstance(video, str):
                if video.startswith('http'):
                    async with httpx.AsyncClient() as client:
                        response = await client.get(video)
                        response.raise_for_status()
                        return response.content
                else:
                    with open(video, 'rb') as f:
                        return f.read()
            
            raise ValueError(f"Unexpected video type: {type(video)}")
            
        except Exception as e:
            logger.error(f"LTX-Video generation failed: {e}")
            raise
    
    async def _generate_with_svd(
        self,
        image_bytes: bytes,
        prompt: str,
        duration: int = 5,
    ) -> bytes:
        """
        Generate video using Stable Video Diffusion (fallback)
        
        Args:
            image_bytes: Input image as bytes
            prompt: Motion/action prompt (less effective for SVD)
            duration: Video duration
            
        Returns:
            Video bytes
        """
        try:
            # SVD uses different API endpoint
            loop = asyncio.get_event_loop()
            video = await loop.run_in_executor(
                None,
                lambda: self.fallback_client.image_to_video(
                    image_bytes,
                    model=settings.VIDEO_MODEL_FALLBACK,
                )
            )
            
            # Handle response
            if isinstance(video, bytes):
                return video
            
            if hasattr(video, 'read'):
                return video.read()
            
            if isinstance(video, str):
                if video.startswith('http'):
                    async with httpx.AsyncClient() as client:
                        response = await client.get(video)
                        response.raise_for_status()
                        return response.content
                else:
                    with open(video, 'rb') as f:
                        return f.read()
            
            raise ValueError(f"Unexpected video type: {type(video)}")
            
        except Exception as e:
            logger.error(f"SVD generation failed: {e}")
            raise
    
    async def generate_video_from_text(
        self,
        prompt: str,
        duration: int = 5,
        model: str = "veo",  # veo, modelscope, or specific model name
    ) -> bytes:
        """
        Generate video directly from text prompt
        
        Args:
            prompt: Text description of the video
            duration: Video duration in seconds
            model: Text-to-video model to use (veo, modelscope, etc.)
            
        Returns:
            Video bytes
        """
        try:
            logger.info(f"Generating video from text using {model}")
            logger.info(f"Prompt: {prompt}")
            
            # Try Google Veo 3.1 first (best quality)
            if model == "veo" or model == "veo-3.1":
                if self.veo_client:
                    try:
                        return await self._generate_with_veo(prompt, duration)
                    except Exception as veo_error:
                        logger.warning(f"Veo failed, falling back to HuggingFace: {veo_error}")
                        # Continue to fallback
                else:
                    logger.warning("Veo not available, falling back to HuggingFace")
            
            # Fallback to HuggingFace models
            model_name = model if model not in ["veo", "modelscope"] else "damo-vilab/text-to-video-ms-1.7b"
            
            # Use text-to-video model
            loop = asyncio.get_event_loop()
            video = await loop.run_in_executor(
                None,
                lambda: self.fallback_client.text_to_video(
                    prompt,
                    model=model_name,
                )
            )
            
            # Handle response
            if isinstance(video, bytes):
                return video
            
            if hasattr(video, 'read'):
                return video.read()
            
            if isinstance(video, str):
                if video.startswith('http'):
                    async with httpx.AsyncClient() as client:
                        response = await client.get(video)
                        response.raise_for_status()
                        return response.content
                else:
                    with open(video, 'rb') as f:
                        return f.read()
            
            raise ValueError(f"Unexpected video type: {type(video)}")
            
        except Exception as e:
            logger.error(f"Text-to-video generation failed: {e}")
            raise
    
    async def _generate_with_veo(
        self,
        prompt: str,
        duration: int = 5,
    ) -> bytes:
        """
        Generate video using Google Veo 3.1
        
        Args:
            prompt: Text description
            duration: Video duration in seconds
            
        Returns:
            Video bytes
        """
        try:
            logger.info("Using Google Veo 3.1 for text-to-video generation")
            
            # Start video generation operation
            loop = asyncio.get_event_loop()
            operation = await loop.run_in_executor(
                None,
                lambda: self.veo_client.models.generate_videos(
                    model="veo-3.1-generate-preview",
                    prompt=prompt,
                )
            )
            
            # Poll until complete (with timeout)
            max_wait_time = 300  # 5 minutes max
            start_time = time.time()
            poll_interval = 10  # Check every 10 seconds
            
            while not operation.done:
                if time.time() - start_time > max_wait_time:
                    raise TimeoutError("Video generation timed out after 5 minutes")
                
                logger.info(f"Waiting for Veo generation... ({int(time.time() - start_time)}s)")
                await asyncio.sleep(poll_interval)
                
                # Refresh operation status
                operation = await loop.run_in_executor(
                    None,
                    lambda: self.veo_client.operations.get(operation)
                )
            
            # Get generated video
            generated_video = operation.response.generated_videos[0]
            
            # Download video bytes
            video_file = await loop.run_in_executor(
                None,
                lambda: self.veo_client.files.download(file=generated_video.video)
            )
            
            # Read bytes
            if hasattr(video_file, 'read'):
                return video_file.read()
            elif isinstance(video_file, bytes):
                return video_file
            else:
                # Save to temp and read
                temp_path = settings.TEMP_DIR / f"veo_temp_{int(time.time())}.mp4"
                await loop.run_in_executor(
                    None,
                    lambda: generated_video.video.save(str(temp_path))
                )
                with open(temp_path, 'rb') as f:
                    video_bytes = f.read()
                temp_path.unlink()  # Clean up
                return video_bytes
            
        except Exception as e:
            logger.error(f"Veo generation failed: {e}")
            raise
            
            # Use text-to-video model
            loop = asyncio.get_event_loop()
            video = await loop.run_in_executor(
                None,
                lambda: self.fallback_client.text_to_video(
                    prompt,
                    model=model,
                )
            )
            
            # Handle response
            if isinstance(video, bytes):
                return video
            
            if hasattr(video, 'read'):
                return video.read()
            
            if isinstance(video, str):
                if video.startswith('http'):
                    async with httpx.AsyncClient() as client:
                        response = await client.get(video)
                        response.raise_for_status()
                        return response.content
                else:
                    with open(video, 'rb') as f:
                        return f.read()
            
            raise ValueError(f"Unexpected video type: {type(video)}")
            
        except Exception as e:
            logger.error(f"Text-to-video generation failed: {e}")
            raise
    
    async def save_video(
        self,
        video_bytes: bytes,
        output_path: Union[str, Path],
    ) -> Path:
        """
        Save video bytes to file
        
        Args:
            video_bytes: Video content
            output_path: Where to save
            
        Returns:
            Path to saved video
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(video_bytes)
        
        logger.info(f"Video saved to {output_path}")
        return output_path
    
    def get_motion_prompt(self, scene_description: str, scene_narration: str) -> str:
        """
        Generate a motion prompt from scene description
        
        Args:
            scene_description: Visual description
            scene_narration: Narration text
            
        Returns:
            Motion prompt for video generation
        """
        # Extract key actions/movements
        motion_keywords = [
            'dancing', 'jumping', 'running', 'flying', 'spinning',
            'twinkling', 'falling', 'rising', 'waving', 'smiling',
            'moving', 'floating', 'glowing', 'shining', 'swaying'
        ]
        
        # Check for motion words in description
        description_lower = scene_description.lower()
        actions = [kw for kw in motion_keywords if kw in description_lower]
        
        if actions:
            # Build prompt emphasizing the motion
            action_text = ', '.join(actions)
            return f"{scene_narration}. The scene shows {action_text}, gentle movement, smooth animation"
        else:
            # Generic motion prompt
            return f"{scene_narration}. Gentle camera movement, subtle animation, smooth transitions"


# Global service instance
_video_service: Optional[VideoGenerationService] = None


def get_video_service() -> VideoGenerationService:
    """Get or create video generation service"""
    global _video_service
    if _video_service is None:
        _video_service = VideoGenerationService()
    return _video_service


# Convenience functions
async def generate_video_from_image(
    image_path: Union[str, Path],
    prompt: str,
    output_path: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Generate video from image and save
    
    Args:
        image_path: Input image path
        prompt: Motion prompt
        output_path: Where to save (optional)
        
    Returns:
        Path to generated video
    """
    service = get_video_service()
    
    # Generate video
    video_bytes, model_used = await service.generate_video_from_image(
        image_path=image_path,
        prompt=prompt,
    )
    
    # Determine output path
    if output_path is None:
        image_path = Path(image_path)
        output_path = settings.TEMP_DIR / f"{image_path.stem}_video.mp4"
    
    # Save video
    return await service.save_video(video_bytes, output_path)


async def generate_video_from_text(
    prompt: str,
    output_path: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Generate video from text and save
    
    Args:
        prompt: Text description
        output_path: Where to save (optional)
        
    Returns:
        Path to generated video
    """
    service = get_video_service()
    
    # Generate video
    video_bytes = await service.generate_video_from_text(prompt)
    
    # Determine output path
    if output_path is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = settings.TEMP_DIR / f"video_{timestamp}.mp4"
    
    # Save video
    return await service.save_video(video_bytes, output_path)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        """Test video generation"""
        service = get_video_service()
        
        # Test with a sample image (you need to provide one)
        test_image = Path("test_image.png")
        if test_image.exists():
            print("Testing image-to-video...")
            video_path = await generate_video_from_image(
                test_image,
                prompt="The character starts to dance and smile",
            )
            print(f"Video generated: {video_path}")
        else:
            print(f"Test image not found: {test_image}")
    
    asyncio.run(test())
