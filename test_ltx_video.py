"""
Test Script for LTX-Video Integration
Quick test to verify video generation works
"""
import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from PIL import Image
from app.services.video_service import get_video_service
from app.config import settings


def create_test_image():
    """Create a simple test image"""
    # Create a colorful gradient image
    img = Image.new('RGB', (512, 512))
    pixels = img.load()
    
    for i in range(512):
        for j in range(512):
            # Create a star-like gradient
            r = int((i / 512) * 255)
            g = int((j / 512) * 255)
            b = int(((i + j) / 1024) * 255)
            pixels[i, j] = (r, g, b)
    
    test_path = settings.TEMP_DIR / "test_star.png"
    img.save(test_path)
    print(f"✅ Test image created: {test_path}")
    return test_path


async def test_ltx_video():
    """Test LTX-Video generation"""
    print("\n" + "=" * 60)
    print("🎬 Testing LTX-Video Integration")
    print("=" * 60)
    
    # Check HuggingFace token
    if not settings.HUGGINGFACE_TOKEN:
        print("❌ Error: HUGGINGFACE_TOKEN not found in .env")
        print("   Get token from: https://huggingface.co/settings/tokens")
        return False
    
    print(f"✅ HuggingFace token configured")
    print(f"✅ Video model: {settings.VIDEO_MODEL}")
    print(f"✅ Fallback model: {settings.VIDEO_MODEL_FALLBACK}")
    print()
    
    try:
        # Create test image
        print("📸 Creating test image...")
        test_image_path = create_test_image()
        
        # Initialize service
        print("🔧 Initializing video service...")
        service = get_video_service()
        print("✅ Video service initialized")
        
        # Generate video
        print("\n🎬 Generating video from image...")
        print("   This may take 1-3 minutes...")
        print(f"   Prompt: 'A twinkling star in the night sky, gentle glow'")
        
        video_bytes, model_used = await service.generate_video_from_image(
            image_path=test_image_path,
            prompt="A twinkling star in the night sky, gentle glow, magical atmosphere",
            duration=5,
        )
        
        # Save video
        output_path = settings.VIDEOS_DIR / "test_ltx_video.mp4"
        saved_path = await service.save_video(video_bytes, output_path)
        
        # Check file size
        file_size = saved_path.stat().st_size / (1024 * 1024)  # MB
        
        print()
        print("=" * 60)
        print("✅ SUCCESS! Video generated successfully!")
        print("=" * 60)
        print(f"📁 Video saved to: {saved_path}")
        print(f"📊 File size: {file_size:.2f} MB")
        print(f"🎨 Model used: {model_used}")
        print(f"⏱️  Duration: ~5 seconds")
        print()
        print("🎉 LTX-Video integration is working!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR: Video generation failed")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("Possible solutions:")
        print("1. Check HuggingFace token is valid")
        print("2. Verify internet connection")
        print("3. HuggingFace API might be under heavy load (try again)")
        print("4. Check if LTX-Video model is accessible")
        print()
        
        import traceback
        traceback.print_exc()
        
        return False


def main():
    """Main test function"""
    print("\n🚀 Starting LTX-Video Test\n")
    
    # Run async test
    success = asyncio.run(test_ltx_video())
    
    if success:
        print("\n✅ All tests passed! Ready to generate videos.")
        print("\nNext steps:")
        print("1. Add GOOGLE_API_KEY to .env for LLM scene generation")
        print("2. Run: python run.py")
        print("3. Open: http://localhost:7860")
    else:
        print("\n❌ Tests failed. Please fix the errors above.")
        print("\nNeed help? Check:")
        print("- IMPLEMENTATION_GUIDE.md")
        print("- README.md")
    
    print()


if __name__ == "__main__":
    main()
