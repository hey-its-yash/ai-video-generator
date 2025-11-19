"""
Video Editor Service
Handles video assembly, audio merging, and final rendering using MoviePy
"""
import os
import logging
from pathlib import Path
from typing import List, Optional

from moviepy.editor import (
    VideoFileClip, 
    AudioFileClip, 
    concatenate_videoclips, 
    CompositeAudioClip,
    vfx,
    afx
)
import moviepy.video.fx.all as vfx_all

from app.config import settings
from app.models.schemas import Scene
from app.utils.helpers import sanitize_filename

logger = logging.getLogger(__name__)

class VideoEditorService:
    """
    Service for assembling final videos from scenes and audio.
    Uses MoviePy for video editing.
    """
    
    def __init__(self):
        self.output_dir = settings.VIDEOS_DIR
        self.temp_dir = settings.TEMP_DIR
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def assemble_video(
        self,
        scenes: List[Scene],
        output_filename: str,
        background_music: Optional[str] = None
    ) -> Path:
        """
        Assemble a final video from a list of scenes.
        
        Args:
            scenes: List of Scene objects with video_path and audio_path set
            output_filename: Name of the output file
            background_music: Optional path to background music file
            
        Returns:
            Path to the generated video file
        """
        try:
            logger.info(f"Assembling video from {len(scenes)} scenes...")
            
            clips = []
            
            for i, scene in enumerate(scenes):
                if not scene.video_path or not Path(scene.video_path).exists():
                    logger.warning(f"Scene {i+1} missing video path, skipping")
                    continue
                    
                # Load video
                video_clip = VideoFileClip(scene.video_path)
                
                # Load audio if available
                if scene.audio_path and Path(scene.audio_path).exists():
                    audio_clip = AudioFileClip(scene.audio_path)
                    
                    # Adjust video duration to match audio
                    # If video is shorter, loop it
                    # If video is longer, trim it (or speed it up?)
                    # For now, we'll loop video if shorter, or trim if longer
                    
                    if video_clip.duration < audio_clip.duration:
                        # Loop video to match audio duration
                        video_clip = video_clip.loop(duration=audio_clip.duration)
                    else:
                        # Trim video to match audio duration
                        video_clip = video_clip.subclip(0, audio_clip.duration)
                        
                    video_clip = video_clip.set_audio(audio_clip)
                else:
                    logger.warning(f"Scene {i+1} missing audio, using silent video")
                
                # Add crossfade transition (optional, but looks nice)
                # video_clip = video_clip.crossfadein(0.5)
                
                clips.append(video_clip)
            
            if not clips:
                raise ValueError("No valid clips to assemble")
            
            # Concatenate all clips
            final_clip = concatenate_videoclips(clips, method="compose")
            
            # Add background music if provided
            if background_music and Path(background_music).exists():
                final_clip = self._add_background_music(final_clip, background_music)
            
            # Output path
            safe_filename = sanitize_filename(output_filename)
            if not safe_filename.endswith('.mp4'):
                safe_filename += '.mp4'
            output_path = self.output_dir / safe_filename
            
            logger.info(f"Rendering final video to {output_path}...")
            
            # Write video file
            # fps=24 is standard for animation
            # codec='libx264' is standard MP4
            # audio_codec='aac' is standard audio
            final_clip.write_videofile(
                str(output_path),
                fps=24,
                codec='libx264',
                audio_codec='aac',
                threads=4,
                logger=None  # Disable moviepy's own logger to keep console clean
            )
            
            # Close clips to release resources
            final_clip.close()
            for clip in clips:
                clip.close()
                
            logger.info("Video assembly completed successfully")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to assemble video: {e}")
            raise

    def _add_background_music(self, video_clip, music_path, volume=0.1):
        """Add background music to the video clip"""
        try:
            music_clip = AudioFileClip(music_path)
            
            # Loop music if shorter than video
            if music_clip.duration < video_clip.duration:
                music_clip = afx.audio_loop(music_clip, duration=video_clip.duration)
            else:
                music_clip = music_clip.subclip(0, video_clip.duration)
                
            # Lower volume of background music
            music_clip = music_clip.volumex(volume)
            
            # Combine with original audio (narration)
            final_audio = CompositeAudioClip([video_clip.audio, music_clip])
            video_clip = video_clip.set_audio(final_audio)
            
            return video_clip
            
        except Exception as e:
            logger.warning(f"Failed to add background music: {e}")
            return video_clip
