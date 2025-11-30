"""
Direct Video Generation Pipeline (PARALLEL)
Poem → Scenes → Videos + Audio (parallel) → Final Video

This script generates videos from scene descriptions with parallel processing for speed.
"""
import asyncio
import logging
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.services.llm_service import get_llm_service
from app.services.video_service import get_video_service
from app.services.audio_service import AudioService
from app.services.video_editor import VideoEditorService
from app.services.scene_builder import SceneBuilder
from app.models.schemas import Scene


class VideoPipeline:
    """
    Parallel video generation pipeline:
    Poem → Scenes → Videos + Audio (PARALLEL) → Final Video
    """
    
    def __init__(self, max_parallel_videos: int = 3):
        self.llm_service = get_llm_service()
        self.video_service = get_video_service()
        self.audio_service = AudioService()
        self.video_editor = VideoEditorService()
        self.scene_builder = SceneBuilder()  # For enhanced prompt generation
        self.max_parallel_videos = max_parallel_videos
        
        # Ensure output directories exist
        settings.VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
        settings.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    async def generate(
        self,
        poem_text: str,
        num_scenes: int = 4,
        style: str = "children_book",
        output_name: str = None,
        parallel: bool = True,
    ) -> Path:
        """
        Generate a complete video from a poem with parallel processing.
        
        Args:
            poem_text: The poem/rhyme text
            num_scenes: Number of scenes to generate (3-10)
            style: Visual style preset
            output_name: Output filename (optional)
            parallel: Enable parallel video/audio generation
            
        Returns:
            Path to the final video
        """
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = output_name or f"poem_video_{timestamp}"
        
        print("\n" + "="*60)
        print("🎬 VIDEO GENERATION PIPELINE" + (" (PARALLEL MODE)" if parallel else ""))
        print("="*60)
        
        # Step 1: Generate scenes from poem
        print("\n📝 Step 1: Generating scenes from poem...")
        step1_start = time.time()
        scenes_result = await self.llm_service.generate_scenes(
            rhyme_text=poem_text,
            num_scenes=num_scenes,
            style=style,
        )
        step1_time = time.time() - step1_start
        
        print(f"   ✓ Generated {len(scenes_result.scenes)} scenes ({step1_time:.1f}s)")
        print(f"   Title: {scenes_result.title}")
        
        # Step 2: Generate videos and audio for each scene
        print("\n🎥 Step 2: Generating videos and audio...")
        step2_start = time.time()
        
        if parallel:
            # PARALLEL: Generate all videos and audio concurrently
            await self._generate_all_parallel(scenes_result.scenes, style, timestamp)
        else:
            # SEQUENTIAL: Original behavior
            await self._generate_all_sequential(scenes_result.scenes, style, timestamp)
        
        step2_time = time.time() - step2_start
        print(f"\n   ⏱️ Total generation time: {step2_time:.1f}s")
        
        # Step 3: Assemble final video
        print("\n🎞️ Step 3: Assembling final video...")
        step3_start = time.time()
        
        # Filter scenes that have both video and audio
        valid_scenes = [s for s in scenes_result.scenes if s.video_path and s.audio_path]
        
        if not valid_scenes:
            raise ValueError("No valid scenes with video and audio to assemble")
        
        print(f"   Assembling {len(valid_scenes)} scenes...")
        
        final_video_path = self.video_editor.assemble_video(
            scenes=valid_scenes,
            output_filename=output_name,
        )
        step3_time = time.time() - step3_start
        
        total_time = time.time() - start_time
        
        print(f"\n" + "="*60)
        print(f"✅ VIDEO GENERATION COMPLETE!")
        print(f"📁 Output: {final_video_path}")
        print(f"⏱️ Time breakdown:")
        print(f"   Scene generation: {step1_time:.1f}s")
        print(f"   Video/Audio gen:  {step2_time:.1f}s")
        print(f"   Assembly:         {step3_time:.1f}s")
        print(f"   TOTAL:            {total_time:.1f}s")
        print("="*60 + "\n")
        
        return final_video_path
    
    async def _generate_all_parallel(
        self,
        scenes: List[Scene],
        style: str,
        timestamp: str
    ):
        """
        Generate all videos and audio in parallel.
        
        Strategy:
        1. Start all video generation tasks concurrently
        2. Start all audio generation tasks concurrently
        3. Wait for all to complete
        """
        print(f"   🚀 Parallel mode: Processing {len(scenes)} scenes concurrently...")
        
        # Create tasks for video and audio generation
        video_tasks = []
        audio_tasks = []
        
        for i, scene in enumerate(scenes):
            # Video task
            video_task = self._generate_scene_video(scene, i, style, timestamp)
            video_tasks.append(video_task)
            
            # Audio task
            audio_task = self._generate_scene_audio(scene, i, timestamp)
            audio_tasks.append(audio_task)
        
        # Run all video and audio tasks concurrently
        print(f"   📹 Starting {len(video_tasks)} video tasks...")
        print(f"   🔊 Starting {len(audio_tasks)} audio tasks...")
        
        # Gather all tasks - videos and audio run in parallel
        all_tasks = video_tasks + audio_tasks
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        # Process results
        video_results = results[:len(scenes)]
        audio_results = results[len(scenes):]
        
        # Update scenes with results
        for i, (scene, video_result, audio_result) in enumerate(zip(scenes, video_results, audio_results)):
            if isinstance(video_result, Exception):
                print(f"   ❌ Scene {i+1} video failed: {video_result}")
                scene.video_path = None
            else:
                scene.video_path = video_result
                print(f"   ✓ Scene {i+1} video: {Path(video_result).name}")
            
            if isinstance(audio_result, Exception):
                print(f"   ❌ Scene {i+1} audio failed: {audio_result}")
                scene.audio_path = None
            else:
                scene.audio_path = audio_result
                print(f"   ✓ Scene {i+1} audio: {Path(audio_result).name}")
    
    async def _generate_scene_video(
        self,
        scene: Scene,
        index: int,
        style: str,
        timestamp: str
    ) -> str:
        """Generate video for a single scene."""
        try:
            video_prompt = self._create_video_prompt(scene, style)
            video_bytes = await self.video_service.generate_video_from_text(
                prompt=video_prompt,
                duration=int(scene.duration),
                model="veo",
            )
            
            video_path = settings.TEMP_DIR / f"scene_{index+1}_{timestamp}.mp4"
            await self.video_service.save_video(video_bytes, video_path)
            return str(video_path)
            
        except Exception as e:
            logger.error(f"Video generation failed for scene {index+1}: {e}")
            raise
    
    async def _generate_scene_audio(
        self,
        scene: Scene,
        index: int,
        timestamp: str
    ) -> str:
        """Generate audio for a single scene."""
        try:
            audio_path = await self.audio_service.generate_narration(
                text=scene.narration,
                filename=f"scene_{index+1}_{timestamp}",
            )
            return str(audio_path)
            
        except Exception as e:
            logger.error(f"Audio generation failed for scene {index+1}: {e}")
            raise
    
    async def _generate_all_sequential(
        self,
        scenes: List[Scene],
        style: str,
        timestamp: str
    ):
        """Generate all videos and audio sequentially (original behavior)."""
        for i, scene in enumerate(scenes):
            print(f"\n   Scene {i+1}/{len(scenes)}:")
            print(f"   📖 Narration: {scene.narration[:50]}...")
            
            # Generate video
            try:
                print(f"   🎬 Generating video...")
                video_prompt = self._create_video_prompt(scene, style)
                video_bytes = await self.video_service.generate_video_from_text(
                    prompt=video_prompt,
                    duration=int(scene.duration),
                    model="veo",
                )
                
                video_path = settings.TEMP_DIR / f"scene_{i+1}_{timestamp}.mp4"
                await self.video_service.save_video(video_bytes, video_path)
                scene.video_path = str(video_path)
                print(f"   ✓ Video saved: {video_path.name}")
                
            except Exception as e:
                logger.error(f"Video generation failed for scene {i+1}: {e}")
                print(f"   ❌ Video generation failed: {e}")
                scene.video_path = None
                continue
            
            # Generate audio
            try:
                print(f"   🔊 Generating audio...")
                audio_path = await self.audio_service.generate_narration(
                    text=scene.narration,
                    filename=f"scene_{i+1}_{timestamp}",
                )
                scene.audio_path = str(audio_path)
                print(f"   ✓ Audio saved: {audio_path.name}")
                
            except Exception as e:
                logger.error(f"Audio generation failed for scene {i+1}: {e}")
                print(f"   ❌ Audio generation failed: {e}")
                scene.audio_path = None
    
    def _create_video_prompt(self, scene, style: str) -> str:
        """
        Create an enhanced, semantically-aware prompt for video generation.
        Uses SceneBuilder for intelligent keyword extraction and theme detection.
        """
        # Use scene builder for semantic analysis
        keywords = self.scene_builder.extract_keywords(scene.narration)
        theme = self.scene_builder.detect_theme(scene.narration)
        
        # Build enhanced prompt parts
        prompt_parts = []
        
        # 1. Start with the scene description (already enhanced by LLM/SceneBuilder)
        prompt_parts.append(scene.description)
        
        # 2. Add detected mood visuals
        mood_visuals = {
            'joyful': 'bright vibrant colors, warm lighting, happy atmosphere',
            'peaceful': 'soft pastel colors, gentle lighting, serene calm atmosphere',
            'mysterious': 'deep blues and purples, soft glowing lights, enchanting atmosphere',
            'magical': 'sparkles and glowing particles, enchanted lighting, fantasy atmosphere',
            'dreamy': 'soft ethereal colors, glowing light, magical dreamy atmosphere',
        }
        mood_visual = mood_visuals.get(theme.mood.value, mood_visuals['magical'])
        prompt_parts.append(mood_visual)
        
        # 3. Add style-specific modifiers
        style_modifiers = {
            "children_book": "colorful children's book illustration style, cute whimsical characters, soft rounded shapes, storybook aesthetic",
            "watercolor": "soft watercolor painting style, dreamy pastel colors, gentle artistic brushstrokes",
            "cartoon": "bright cartoon animation style, bold outlines, saturated colors, playful animated look",
            "realistic": "photorealistic cinematic style, detailed textures, natural lighting",
            "anime": "beautiful anime art style, expressive eyes, vibrant colors, Japanese animation aesthetic",
            "3d": "high-quality 3D rendered style, Pixar-like quality, smooth professional CGI",
        }
        style_text = style_modifiers.get(style, style_modifiers["children_book"])
        prompt_parts.append(style_text)
        
        # 4. Add motion/action cues from keywords
        if keywords.actions:
            action_text = ", ".join(keywords.actions[:3])
            prompt_parts.append(f"smooth {action_text} motion")
        
        # 5. Add camera movement based on content
        if any(word in scene.narration.lower() for word in ['up', 'above', 'high', 'sky']):
            prompt_parts.append("gentle upward camera pan")
        elif any(word in scene.narration.lower() for word in ['down', 'fall', 'fell']):
            prompt_parts.append("smooth downward camera movement")
        else:
            prompt_parts.append("gentle floating camera movement")
        
        # 6. Add quality modifiers
        prompt_parts.append("professional quality, cinematic lighting, highly detailed animation")
        
        # 7. Add negative prompt to avoid artifacts
        negative_elements = [
            "no text", "no watermarks", "no logos", "no modern elements",
            "no distortion", "no blurry", "no low quality"
        ]
        prompt_parts.append(f"Negative: {', '.join(negative_elements)}")
        
        return ". ".join(prompt_parts)


async def main():
    """Main function to run the pipeline"""
    
    example_poems = {
        "twinkle": """Twinkle, twinkle, little star,
How I wonder what you are.
Up above the world so high,
Like a diamond in the sky.""",
        
        "humpty": """Humpty Dumpty sat on a wall,
Humpty Dumpty had a great fall.
All the king's horses and all the king's men,
Couldn't put Humpty together again.""",
        
        "rain": """Rain, rain, go away,
Come again another day.
Little Johnny wants to play,
Rain, rain, go away.""",
    }
    
    print("\n🎬 AI Video Generator - Parallel Pipeline")
    print("="*50)
    print("\nExample poems available:")
    for key in example_poems:
        print(f"  - {key}")
    
    print("\nEnter your poem (or type an example name, or 'quit' to exit):")
    print("(End input with an empty line)")
    
    lines = []
    while True:
        try:
            line = input()
            if line.lower() == 'quit':
                print("Goodbye!")
                return
            if line.lower() in example_poems:
                poem_text = example_poems[line.lower()]
                break
            if line == '' and lines:
                poem_text = '\n'.join(lines)
                break
            lines.append(line)
        except EOFError:
            if lines:
                poem_text = '\n'.join(lines)
            else:
                poem_text = example_poems["twinkle"]
            break
    
    print(f"\n📜 Using poem:\n{poem_text}\n")
    
    pipeline = VideoPipeline()
    
    try:
        final_video = await pipeline.generate(
            poem_text=poem_text,
            num_scenes=4,
            style="children_book",
            parallel=True,  # Enable parallel processing
        )
        print(f"\n🎉 Success! Your video is ready at:\n{final_video}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.exception("Pipeline failed")


if __name__ == "__main__":
    asyncio.run(main())
