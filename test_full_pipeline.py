"""
End-to-End Pipeline Test
Generates a complete video from text using all services.
"""
import asyncio
import sys
import os
from pathlib import Path
import logging
import time

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.services.llm_service import LLMService
from app.services.audio_service import AudioService
from app.services.video_service import VideoGenerationService
from app.services.video_editor import VideoEditorService
from app.models.schemas import Scene

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_pipeline():
    print("\n" + "="*80)
    print("🚀 STARTING END-TO-END VIDEO GENERATION TEST")
    print("="*80)
    
    # ---------------------------------------------------------
    # 0. INITIALIZATION
    # ---------------------------------------------------------
    print("\n[0/4] Initializing Services...")
    try:
        llm_service = LLMService()
        audio_service = AudioService()
        video_service = VideoGenerationService()
        editor_service = VideoEditorService()
        print("   ✓ All services initialized")
    except Exception as e:
        print(f"   ✗ Initialization failed: {e}")
        return

    # Test Data - Short rhyme to save time/credits
    rhyme_text = """
    Twinkle, twinkle, little star,
    How I wonder what you are!
    Up above the world so high,
    Like a diamond in the sky.
    """
    
    job_id = f"test_job_{int(time.time())}"
    print(f"   Job ID: {job_id}")

    # ---------------------------------------------------------
    # 1. SCENE GENERATION (LLM)
    # ---------------------------------------------------------
    print("\n[1/4] Generating Scenes (LLM)...")
    try:
        scene_result = await llm_service.generate_scenes(rhyme_text)
        scenes = scene_result.scenes
        
        # Limit to 2 scenes for testing if LLM generates too many
        if len(scenes) > 2:
            print(f"   ℹ Limiting from {len(scenes)} to 2 scenes for testing")
            scenes = scenes[:2]
            
        print(f"   ✓ Generated {len(scenes)} scenes:")
        for s in scenes:
            print(f"     - Scene {s.scene_number}: {s.description[:50]}...")
            
    except Exception as e:
        print(f"   ✗ Scene generation failed: {e}")
        return

    # ---------------------------------------------------------
    # 2. ASSET GENERATION (Audio & Video)
    # ---------------------------------------------------------
    print("\n[2/4] Generating Assets...")
    
    for i, scene in enumerate(scenes):
        print(f"\n   Processing Scene {scene.scene_number}...")
        
        # A. Generate Audio
        try:
            print("     Creating Audio...")
            audio_filename = f"{job_id}_scene_{scene.scene_number}"
            audio_path = await audio_service.generate_narration(
                text=scene.narration,
                filename=audio_filename
            )
            scene.audio_path = str(audio_path)
            
            # Get duration to inform video generation
            audio_duration = await audio_service.get_audio_duration(audio_path)
            scene.duration = max(audio_duration, 3.0) # Minimum 3 seconds
            print(f"     ✓ Audio created ({audio_duration:.1f}s)")
            
        except Exception as e:
            print(f"     ✗ Audio failed: {e}")
            continue

        # B. Generate Video
        try:
            print(f"     Creating Video (Prompt: {scene.description[:30]}...)...")
            # Use Text-to-Video (Veo) since we don't have Image Service yet
            video_bytes = await video_service.generate_video_from_text(
                prompt=scene.description,
                duration=int(scene.duration + 1), # Add buffer
                model="veo"
            )
            
            # Save video file
            video_filename = f"{job_id}_scene_{scene.scene_number}.mp4"
            video_path = settings.TEMP_DIR / video_filename
            
            with open(video_path, "wb") as f:
                f.write(video_bytes)
                
            scene.video_path = str(video_path)
            print(f"     ✓ Video created: {video_filename}")
            
        except Exception as e:
            print(f"     ✗ Video failed: {e}")
            # Create a dummy video color clip as fallback so pipeline doesn't crash
            print("     ⚠ Creating dummy fallback video...")
            try:
                from moviepy.editor import ColorClip
                dummy_path = settings.TEMP_DIR / f"{job_id}_scene_{scene.scene_number}_dummy.mp4"
                ColorClip(size=(512, 512), color=(0,0,100), duration=scene.duration).write_videofile(
                    str(dummy_path), fps=24, logger=None
                )
                scene.video_path = str(dummy_path)
            except:
                pass

    # ---------------------------------------------------------
    # 3. ASSEMBLY (Video Editor)
    # ---------------------------------------------------------
    print("\n[3/4] Assembling Final Video...")
    try:
        output_filename = f"final_video_{job_id}"
        final_path = editor_service.assemble_video(
            scenes=scenes,
            output_filename=output_filename
        )
        
        print(f"\n[4/4] SUCCESS! 🎉")
        print(f"   ✓ Final video saved to: {final_path}")
        print(f"   ✓ File size: {final_path.stat().st_size / (1024*1024):.2f} MB")
        
    except Exception as e:
        print(f"   ✗ Assembly failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(run_pipeline())
