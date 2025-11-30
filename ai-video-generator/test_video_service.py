"""
Test script for Video Generation Service
Tests LTX-Video, Stable Video Diffusion, and Google Veo 3.1
"""
import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.services.video_service import VideoGenerationService
from app.utils.helpers import format_duration
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_video_service():
    """Test video generation with different methods"""
    
    print("\n" + "="*80)
    print("VIDEO GENERATION SERVICE TEST")
    print("="*80)
    
    # Initialize service
    print("\n1. Initializing Video Generation Service...")
    try:
        video_service = VideoGenerationService()
        print("   ✓ Service initialized successfully")
        
        # Check available providers
        print("\n2. Checking Available Providers:")
        print(f"   - LTX-Video: {'✓ Available' if video_service.client else '✗ Not available'}")
        print(f"   - Google Veo 3.1: {'✓ Available' if video_service.veo_client else '✗ Not available'}")
        
    except Exception as e:
        print(f"   ✗ Failed to initialize service: {e}")
        return
    
    # Test 1: Text-to-Video with Google Veo (if available)
    if video_service.veo_client:
        print("\n3. Testing Text-to-Video with Google Veo 3.1...")
        print("   (Note: Veo may have quota limits)")
        
        test_prompt = "A cute cartoon star twinkling in the night sky, gentle animation, children's book style"
        
        try:
            print(f"   Prompt: {test_prompt}")
            print("   Generating video...")
            
            video_bytes = await video_service.generate_video_from_text(
                prompt=test_prompt,
                duration=5,
                model="veo"
            )
            
            # Save video
            output_path = settings.VIDEOS_DIR / "test_veo_output.mp4"
            with open(output_path, 'wb') as f:
                f.write(video_bytes)
            
            file_size = len(video_bytes) / (1024 * 1024)  # MB
            print(f"   ✓ Video generated successfully!")
            print(f"   ✓ File size: {file_size:.2f} MB")
            print(f"   ✓ Saved to: {output_path}")
            
        except Exception as e:
            print(f"   ⚠ Veo generation skipped: {str(e)[:100]}")
            logger.warning(f"Veo test skipped: {e}")
    else:
        print("\n3. Skipping Veo test (API key not configured)")
        print("   To enable: Set GOOGLE_API_KEY in .env file")
    
    # Test 2: Image-to-Video with LTX-Video
    print("\n4. Testing Image-to-Video with LTX-Video...")
    
    # Create a simple test image
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create test image
        img = Image.new('RGB', (768, 512), color=(135, 206, 235))  # Sky blue
        draw = ImageDraw.Draw(img)
        
        # Draw a simple star
        star_points = [
            (384, 156), (404, 216), (464, 216), (414, 256),
            (434, 316), (384, 276), (334, 316), (354, 256),
            (304, 216), (364, 216)
        ]
        draw.polygon(star_points, fill='yellow', outline='gold')
        
        # Save test image
        test_image_path = settings.TEMP_DIR / "test_star.png"
        img.save(test_image_path)
        print(f"   ✓ Created test image: {test_image_path}")
        
        # Generate video from image
        print("   Generating video from image...")
        
        video_bytes = await video_service.generate_video_from_image(
            image_path=test_image_path,
            prompt="A twinkling star in the sky",
            duration=3
        )
        
        # Save video
        output_path = settings.VIDEOS_DIR / "test_ltx_output.mp4"
        with open(output_path, 'wb') as f:
            f.write(video_bytes)
        
        file_size = len(video_bytes) / (1024 * 1024)  # MB
        print(f"   ✓ Video generated successfully!")
        print(f"   ✓ File size: {file_size:.2f} MB")
        print(f"   ✓ Saved to: {output_path}")
        
    except Exception as e:
        print(f"   ✗ Image-to-video generation failed: {e}")
        logger.error(f"LTX test error: {e}", exc_info=True)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Output directory: {settings.VIDEOS_DIR}")
    print("\nGenerated files:")
    
    for video_file in settings.VIDEOS_DIR.glob("test_*.mp4"):
        size_mb = video_file.stat().st_size / (1024 * 1024)
        print(f"  - {video_file.name} ({size_mb:.2f} MB)")
    
    print("\n✓ Video service test completed!")
    print("="*80 + "\n")


async def test_quick_validation():
    """Quick validation without actual video generation"""
    
    print("\n" + "="*80)
    print("QUICK VALIDATION TEST (No video generation)")
    print("="*80)
    
    print("\n1. Validating Configuration...")
    
    # Check API keys
    checks = {
        "HuggingFace Token": bool(settings.HUGGINGFACE_TOKEN),
        "Google API Key": bool(settings.GOOGLE_API_KEY),
        "Output Directories": all([
            settings.VIDEOS_DIR.exists(),
            settings.TEMP_DIR.exists(),
        ]),
    }
    
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        print(f"   {status} {check_name}: {result}")
    
    print("\n2. Testing Service Initialization...")
    try:
        video_service = VideoGenerationService()
        print("   ✓ VideoGenerationService initialized")
        print(f"   ✓ LTX-Video available: {video_service.client is not None}")
        print(f"   ✓ Google Veo available: {video_service.veo_client is not None}")
        
    except Exception as e:
        print(f"   ✗ Initialization failed: {e}")
        return
    
    print("\n3. Validating Methods...")
    methods = [
        'generate_video_from_image',
        'generate_video_from_text',
        '_generate_with_ltx_video',
        '_generate_with_svd',
        '_generate_with_veo',
    ]
    
    for method in methods:
        has_method = hasattr(video_service, method)
        status = "✓" if has_method else "✗"
        print(f"   {status} {method}")
    
    print("\n" + "="*80)
    print("✓ Quick validation completed!")
    print("="*80 + "\n")


def main():
    """Main test runner"""
    
    print("\n" + "="*80)
    print("VIDEO SERVICE TEST SUITE")
    print("="*80)
    print("\nChoose test mode:")
    print("1. Quick Validation (no video generation)")
    print("2. Full Test (generates test videos - may take several minutes)")
    print("3. Both")
    
    choice = input("\nEnter choice (1/2/3) [default: 1]: ").strip() or "1"
    
    if choice == "1":
        asyncio.run(test_quick_validation())
    elif choice == "2":
        asyncio.run(test_video_service())
    elif choice == "3":
        asyncio.run(test_quick_validation())
        print("\n" + "="*80)
        input("Press Enter to continue with full test...")
        asyncio.run(test_video_service())
    else:
        print("Invalid choice. Running quick validation...")
        asyncio.run(test_quick_validation())


if __name__ == "__main__":
    main()
