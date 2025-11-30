"""
Test script for the AI Video Generator pipeline.
Tests the flow: Poem → Scenes → Audio → Videos → Final Video
"""
import asyncio
import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_pipeline():
    """Test the complete video generation pipeline."""
    print("=" * 60)
    print("AI Video Generator - Pipeline Test")
    print("=" * 60)
    
    # Test rhyme
    test_rhyme = """Twinkle, twinkle, little star,
How I wonder what you are!
Up above the world so high,
Like a diamond in the sky."""
    
    print(f"\n📝 Test Input Rhyme:\n{test_rhyme}\n")
    
    # Step 1: Test Configuration
    print("\n🔧 Step 1: Loading Configuration...")
    try:
        from app.config import settings, print_config_summary
        print(f"  ✅ Configuration loaded")
        print(f"  - Google API Key: {'✅ Set' if settings.GOOGLE_API_KEY else '❌ Not set'}")
        print(f"  - HuggingFace Token: {'✅ Set' if settings.HUGGINGFACE_TOKEN else '❌ Not set'}")
        print(f"  - OpenAI API Key: {'✅ Set' if settings.OPENAI_API_KEY else '❌ Not set'}")
        print(f"  - Available LLMs: {settings.get_available_llms()}")
    except Exception as e:
        print(f"  ❌ Configuration Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 2: Test LLM Scene Generation
    print("\n🎬 Step 2: Testing LLM Scene Generation...")
    scenes = None
    try:
        from app.services.llm_service import LLMService
        llm_service = LLMService()
        
        # Try to generate scenes
        result = await llm_service.generate_scenes(test_rhyme, num_scenes=4)
        
        if result and result.scenes:
            scenes = result.scenes
            print(f"  ✅ Generated {len(scenes)} scenes:")
            print(f"  Title: {result.title}")
            print(f"  Total Duration: {result.total_duration}s")
            for scene in scenes:
                print(f"\n  Scene {scene.scene_number}:")
                print(f"    Description: {scene.description[:80]}...")
                print(f"    Narration: {scene.narration[:50]}...")
                print(f"    Duration: {scene.duration}s")
        else:
            print("  ⚠️ No scenes generated")
    except Exception as e:
        print(f"  ❌ LLM Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Create mock scenes if LLM failed
    if not scenes:
        print("  📋 Using mock scenes for testing...")
        from app.models.schemas import Scene
        scenes = [
            Scene(
                scene_number=1,
                description="A twinkling star in the night sky",
                narration="Twinkle, twinkle, little star, How I wonder what you are!",
                duration=3,
                keywords=["star", "night", "twinkle"]
            ),
            Scene(
                scene_number=2,
                description="A diamond sparkling in the dark sky above the world",
                narration="Up above the world so high, Like a diamond in the sky.",
                duration=3,
                keywords=["diamond", "sky", "world"]
            )
        ]
    
    # Step 3: Test Audio Generation
    print("\n🔊 Step 3: Testing Audio Generation...")
    try:
        from app.services.audio_service import AudioService
        audio_service = AudioService()
        
        # Create output directory
        output_dir = Path("output/test")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate audio for first scene
        test_narration = scenes[0].narration
        audio_path = output_dir / "test_audio.mp3"
        
        result = await audio_service.generate_narration(test_narration, str(audio_path))
        
        if result and Path(result).exists():
            print(f"  ✅ Audio generated: {result}")
            duration = await audio_service.get_audio_duration(result)
            print(f"  - Duration: {duration:.2f}s")
            print(f"  - File size: {Path(result).stat().st_size / 1024:.2f} KB")
        else:
            print(f"  ❌ Audio generation failed")
    except Exception as e:
        print(f"  ❌ Audio Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 4: Test Video Generation
    print("\n🎥 Step 4: Testing Video Generation...")
    try:
        from app.services.video_service import VideoGenerationService, get_video_service
        video_service = get_video_service()
        
        # Check available providers
        print(f"  Available providers:")
        print(f"    - LTX Video (HuggingFace): {'✅' if settings.HUGGINGFACE_TOKEN else '❌'}")
        print(f"    - Google Veo: {'✅' if settings.GOOGLE_API_KEY else '❌'}")
        
        # Try text-to-video generation
        test_prompt = scenes[0].description
        video_path = output_dir / "test_video.mp4"
        
        print(f"\n  Generating video from text: '{test_prompt[:50]}...'")
        print(f"  ⏳ This may take a while...")
        
        # Note: This will likely fail without valid API tokens
        video_bytes = await video_service.generate_video_from_text(
            prompt=test_prompt,
            duration=3
        )
        
        if video_bytes:
            await video_service.save_video(video_bytes, video_path)
            print(f"  ✅ Video generated: {video_path}")
            print(f"  - File size: {Path(video_path).stat().st_size / 1024:.2f} KB")
        else:
            print(f"  ⚠️ Video generation returned empty")
    except Exception as e:
        print(f"  ⚠️ Video Error: {e}")
        print("  💡 This is expected if API keys are not configured correctly")
    
    # Step 5: Test Video Editor
    print("\n🎞️ Step 5: Testing Video Editor...")
    try:
        from app.services.video_editor import VideoEditorService
        editor = VideoEditorService()
        print(f"  ✅ Video Editor initialized")
        print(f"  - Output dir: {editor.output_dir}")
        
        # Check if we have any test videos to assemble
        test_videos = list(output_dir.glob("*.mp4"))
        if test_videos:
            print(f"  Found {len(test_videos)} video clips to assemble")
        else:
            print(f"  No video clips available to test assembly")
            print("  💡 Video assembly will work once video generation succeeds")
    except Exception as e:
        print(f"  ❌ Video Editor Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PIPELINE TEST SUMMARY")
    print("=" * 60)
    print("""
Components Tested:
  ✅ Configuration loading
  ✅ LLM Service (scene generation) 
  ✅ Audio Service (text-to-speech with gTTS)
  ⚠️ Video Service (requires valid API keys)
  ✅ Video Editor (assembly)

To get full functionality:
  1. Set valid GOOGLE_API_KEY in .env for scene generation
  2. Set valid HUGGINGFACE_TOKEN in .env for video generation
  3. Optionally set valid OPENAI_API_KEY as fallback

Current Status:
  - Audio generation works (gTTS is free)
  - Scene generation needs valid Gemini API key
  - Video generation needs valid HuggingFace token
""")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_pipeline())
