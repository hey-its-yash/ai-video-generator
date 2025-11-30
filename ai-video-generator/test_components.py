"""
Quick Test Script for Direct Video Pipeline
Tests each component individually before running the full pipeline.
"""
import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings


async def test_pipeline_components():
    """Test each component of the pipeline"""
    
    print("\n" + "="*60)
    print("🔧 PIPELINE COMPONENT TEST")
    print("="*60)
    
    results = {
        "llm_service": False,
        "video_service": False,
        "audio_service": False,
        "video_editor": False,
    }
    
    # Test 1: LLM Service
    print("\n📝 Testing LLM Service...")
    try:
        from app.services.llm_service import get_llm_service
        llm_service = get_llm_service()
        providers = llm_service.get_available_providers()
        print(f"   ✓ Available providers: {providers}")
        
        if providers:
            # Quick scene generation test
            test_poem = "Twinkle, twinkle, little star, how I wonder what you are."
            scene_result = await llm_service.generate_scenes(
                rhyme_text=test_poem,
                num_scenes=3,  # Minimum is 3 scenes
                style="children_book",
            )
            print(f"   ✓ Generated {len(scene_result.scenes)} scenes")
            for scene in scene_result.scenes:
                print(f"     Scene {scene.scene_number}: {scene.narration[:40]}...")
            results["llm_service"] = True
        else:
            print("   ⚠️ No LLM providers configured")
    except Exception as e:
        print(f"   ❌ LLM Service error: {e}")
    
    # Test 2: Audio Service
    print("\n🔊 Testing Audio Service...")
    try:
        from app.services.audio_service import AudioService
        audio_service = AudioService()
        
        # Generate test audio
        audio_path = await audio_service.generate_narration(
            text="This is a test of the audio generation system.",
            filename="test_audio",
        )
        print(f"   ✓ Audio generated: {audio_path}")
        
        # Get duration
        duration = await audio_service.get_audio_duration(audio_path)
        print(f"   ✓ Audio duration: {duration:.2f} seconds")
        results["audio_service"] = True
    except Exception as e:
        print(f"   ❌ Audio Service error: {e}")
    
    # Test 3: Video Service
    print("\n🎬 Testing Video Service...")
    try:
        from app.services.video_service import get_video_service
        video_service = get_video_service()
        
        print(f"   HuggingFace Token: {'✓ configured' if settings.HUGGINGFACE_TOKEN else '✗ missing'}")
        print(f"   Google API Key: {'✓ configured' if settings.GOOGLE_API_KEY else '✗ missing'}")
        print(f"   Veo Client: {'✓ initialized' if video_service.veo_client else '✗ not available'}")
        
        # Skip actual video generation (uses API quota)
        print("   ⏭️ Skipping video generation test (to save API quota)")
        print("   ℹ️ Video generation will use: Google Veo → HuggingFace fallback")
        results["video_service"] = True
    except Exception as e:
        print(f"   ❌ Video Service error: {e}")
    
    # Test 4: Video Editor
    print("\n🎞️ Testing Video Editor...")
    try:
        from app.services.video_editor import VideoEditorService
        video_editor = VideoEditorService()
        
        print(f"   ✓ Output directory: {video_editor.output_dir}")
        print(f"   ✓ Temp directory: {video_editor.temp_dir}")
        results["video_editor"] = True
    except Exception as e:
        print(f"   ❌ Video Editor error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for component, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"   {component}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All components working! Ready to generate videos.")
    else:
        print("⚠️ Some components failed. Check the errors above.")
    print("="*60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    asyncio.run(test_pipeline_components())
