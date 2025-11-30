"""
Test script for Video Editor Service
Tests video assembly and audio merging
"""
import sys
import os
from pathlib import Path
import logging

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.services.video_editor import VideoEditorService
from app.models.schemas import Scene
from moviepy.editor import ColorClip, AudioFileClip
from gtts import gTTS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_dummy_assets():
    """Create temporary video and audio files for testing"""
    temp_dir = settings.TEMP_DIR
    temp_dir.mkdir(exist_ok=True)
    
    assets = []
    
    # Scene 1: Red background + "Scene One" audio
    vid1_path = temp_dir / "test_scene_1.mp4"
    aud1_path = temp_dir / "test_audio_1.mp3"
    
    logger.info("Creating dummy assets for Scene 1...")
    ColorClip(size=(640, 480), color=(255, 0, 0), duration=3).write_videofile(
        str(vid1_path), fps=24, logger=None
    )
    gTTS("This is scene one.", lang='en').save(str(aud1_path))
    
    assets.append((vid1_path, aud1_path))
    
    # Scene 2: Blue background + "Scene Two" audio
    vid2_path = temp_dir / "test_scene_2.mp4"
    aud2_path = temp_dir / "test_audio_2.mp3"
    
    logger.info("Creating dummy assets for Scene 2...")
    ColorClip(size=(640, 480), color=(0, 0, 255), duration=3).write_videofile(
        str(vid2_path), fps=24, logger=None
    )
    gTTS("This is scene two. It is a bit longer.", lang='en').save(str(aud2_path))
    
    assets.append((vid2_path, aud2_path))
    
    return assets

def test_video_editor():
    print("\n" + "="*80)
    print("VIDEO EDITOR SERVICE TEST")
    print("="*80)
    
    # 1. Initialize Service
    print("\n1. Initializing Video Editor Service...")
    try:
        editor_service = VideoEditorService()
        print("   ✓ Service initialized successfully")
    except Exception as e:
        print(f"   ✗ Failed to initialize service: {e}")
        return

    # 2. Create Dummy Assets
    print("\n2. Creating Dummy Assets...")
    try:
        assets = create_dummy_assets()
        print("   ✓ Dummy assets created")
    except Exception as e:
        print(f"   ✗ Failed to create assets: {e}")
        return

    # 3. Prepare Scenes
    print("\n3. Preparing Scene Objects...")
    scenes = []
    for i, (vid_path, aud_path) in enumerate(assets):
        scene = Scene(
            scene_number=i+1,
            description=f"Test Scene {i+1}",
            narration=f"Narration {i+1}",
            duration=3.0,
            video_path=str(vid_path),
            audio_path=str(aud_path)
        )
        scenes.append(scene)
    print(f"   ✓ Prepared {len(scenes)} scenes")

    # 4. Assemble Video
    print("\n4. Assembling Final Video...")
    output_filename = "test_final_assembly"
    
    try:
        output_path = editor_service.assemble_video(
            scenes=scenes,
            output_filename=output_filename
        )
        
        if output_path.exists():
            print(f"   ✓ Video assembled: {output_path}")
            print(f"   ✓ File size: {output_path.stat().st_size / (1024*1024):.2f} MB")
        else:
            print("   ✗ Output file not found")
            
    except Exception as e:
        print(f"   ✗ Assembly failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*80)
    print("✓ Video editor test completed!")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_video_editor()
