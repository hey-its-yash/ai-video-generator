"""
Audio Generation Service
Handles text-to-speech generation using gTTS (Google Text-to-Speech)
"""
import os
import asyncio
import logging
from pathlib import Path
from typing import Optional, Union

from gtts import gTTS
from moviepy.editor import AudioFileClip
import imageio_ffmpeg

from app.config import settings
from app.utils.helpers import sanitize_filename

logger = logging.getLogger(__name__)

class AudioService:
    """
    Service for generating audio narration from text.
    Uses Google Text-to-Speech (gTTS) which is free.
    """
    
    def __init__(self):
        self.output_dir = settings.AUDIO_DIR
        self.temp_dir = settings.TEMP_DIR
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if ffmpeg is available for pydub
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Check if ffmpeg is available"""
        try:
            # Use imageio-ffmpeg to locate the binary
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            if ffmpeg_path:
                logger.info(f"FFmpeg found at: {ffmpeg_path}")
            else:
                logger.warning("FFmpeg binary not found by imageio-ffmpeg")
        except Exception as e:
            logger.warning(f"FFmpeg setup warning: {e}")

    async def generate_narration(
        self, 
        text: str, 
        filename: str, 
        lang: str = 'en', 
        slow: bool = False
    ) -> Path:
        """
        Generate audio narration from text using gTTS.
        
        Args:
            text: The text to convert to speech
            filename: Output filename (without extension)
            lang: Language code (default: 'en')
            slow: Whether to speak slowly (default: False)
            
        Returns:
            Path to the generated audio file
        """
        try:
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
                
            # Sanitize filename
            safe_filename = sanitize_filename(filename)
            if not safe_filename.endswith('.mp3'):
                safe_filename += '.mp3'
                
            output_path = self.output_dir / safe_filename
            
            # Check if file already exists to avoid re-generating
            if output_path.exists():
                logger.info(f"Audio file already exists: {output_path}")
                return output_path
            
            logger.info(f"Generating narration for: '{text[:30]}...'")
            
            # Run gTTS in a separate thread to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._generate_gtts(text, output_path, lang, slow)
            )
            
            logger.info(f"Audio generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate narration: {e}")
            raise

    def _generate_gtts(self, text: str, output_path: Path, lang: str, slow: bool):
        """Synchronous gTTS generation function"""
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(str(output_path))

    async def get_audio_duration(self, file_path: Union[str, Path]) -> float:
        """
        Get the duration of an audio file in seconds.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Duration in seconds
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            
            # Run pydub in executor as it does file I/O and processing
            loop = asyncio.get_event_loop()
            duration = await loop.run_in_executor(
                None,
                lambda: self._get_duration_sync(file_path)
            )
            
            return duration
            
        except Exception as e:
            logger.error(f"Failed to get audio duration: {e}")
            # Fallback estimate: ~150 words per minute = 2.5 words per second
            # This is just to prevent crashing if ffmpeg fails
            return 5.0 

    def _get_duration_sync(self, file_path: Path) -> float:
        """Synchronous duration check using moviepy"""
        try:
            with AudioFileClip(str(file_path)) as audio:
                return audio.duration
        except Exception as e:
            logger.error(f"MoviePy duration check failed: {e}")
            raise

    async def cleanup_temp_files(self):
        """Clean up temporary audio files"""
        # Implementation for cleanup if needed
        pass
