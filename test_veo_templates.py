"""
Test Google Veo 3.1 with different prompt templates
Tests various children's rhyme scenarios and visual styles
"""
import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.services.video_service import VideoGenerationService
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Test prompt templates
TEST_PROMPTS = [
    {
        "name": "Twinkle Star",
        "prompt": "A cute cartoon star character with a smiling face twinkling brightly in a deep blue night sky, gentle sparkle animation, soft pastel colors, children's book illustration style",
        "duration": 5
    },
    {
        "name": "Moon Rising",
        "prompt": "A gentle crescent moon slowly rising above a peaceful landscape, warm golden glow, dreamy atmosphere, soft clouds drifting, children's storybook animation",
        "duration": 5
    },
    {
        "name": "Sheep Jumping",
        "prompt": "A fluffy white cartoon sheep happily jumping over a wooden fence, cheerful bouncing motion, green grass field, bright sunny day, playful children's animation style",
        "duration": 5
    },
    {
        "name": "Rain Falling",
        "prompt": "Gentle raindrops falling from grey clouds onto a garden with colorful flowers, peaceful rain animation, soft water droplets, children's book watercolor style",
        "duration": 5
    },
    {
        "name": "Stars Dancing",
        "prompt": "Multiple colorful cartoon stars dancing and spinning in the night sky, joyful circular motion, magical sparkles, vibrant children's animation with musical rhythm",
        "duration": 5
    },
    {
        "name": "Boat Sailing",
        "prompt": "A small red sailboat gently rocking on calm blue ocean waves, peaceful sailing motion, seagulls in background, sunny day, children's storybook illustration",
        "duration": 5
    },
]


async def test_single_template(video_service, template_data, index):
    """Test a single prompt template"""
    
    name = template_data["name"]
    prompt = template_data["prompt"]
    duration = template_data["duration"]
    
    print(f"\n{'='*80}")
    print(f"Test {index + 1}/{len(TEST_PROMPTS)}: {name}")
    print(f"{'='*80}")
    print(f"Prompt: {prompt}")
    print(f"Duration: {duration}s")
    print(f"\nGenerating video...")
    
    try:
        # Generate video
        video_bytes = await video_service.generate_video_from_text(
            prompt=prompt,
            duration=duration,
            model="veo"
        )
        
        # Save video
        safe_name = name.lower().replace(" ", "_")
        output_path = settings.VIDEOS_DIR / f"test_veo_{safe_name}.mp4"
        with open(output_path, 'wb') as f:
            f.write(video_bytes)
        
        file_size = len(video_bytes) / (1024 * 1024)  # MB
        print(f"\n✓ SUCCESS!")
        print(f"  File size: {file_size:.2f} MB")
        print(f"  Saved to: {output_path.name}")
        
        return {
            "name": name,
            "success": True,
            "size_mb": file_size,
            "path": output_path
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n✗ FAILED: {error_msg[:150]}")
        
        return {
            "name": name,
            "success": False,
            "error": error_msg
        }


async def test_all_templates():
    """Test all prompt templates"""
    
    print("\n" + "="*80)
    print("GOOGLE VEO 3.1 - TEMPLATE TESTING")
    print("="*80)
    print(f"\nTesting {len(TEST_PROMPTS)} different prompt templates...")
    print("This will take several minutes (each video takes ~60-90 seconds)")
    
    # Initialize service
    print("\nInitializing Video Generation Service...")
    try:
        video_service = VideoGenerationService()
        if not video_service.veo_client:
            print("✗ Google Veo not available. Check API key in .env file")
            return
        print("✓ Service initialized\n")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return
    
    # Test each template
    results = []
    for i, template in enumerate(TEST_PROMPTS):
        result = await test_single_template(video_service, template, i)
        results.append(result)
        
        # Small delay between requests to avoid rate limiting
        if i < len(TEST_PROMPTS) - 1:
            print("\nWaiting 5 seconds before next generation...")
            await asyncio.sleep(5)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"✓ Successful: {len(successful)}")
    print(f"✗ Failed: {len(failed)}")
    
    if successful:
        print("\n✓ Generated Videos:")
        total_size = 0
        for r in successful:
            print(f"  - {r['name']}: {r['size_mb']:.2f} MB ({r['path'].name})")
            total_size += r['size_mb']
        print(f"\n  Total size: {total_size:.2f} MB")
        print(f"  Location: {settings.VIDEOS_DIR}")
    
    if failed:
        print("\n✗ Failed Tests:")
        for r in failed:
            error_short = r['error'][:80] + "..." if len(r['error']) > 80 else r['error']
            print(f"  - {r['name']}: {error_short}")
    
    print("\n" + "="*80)
    print("✓ Template testing completed!")
    print("="*80 + "\n")


async def test_quick_samples():
    """Test just 2-3 quick samples"""
    
    print("\n" + "="*80)
    print("GOOGLE VEO 3.1 - QUICK SAMPLE TEST")
    print("="*80)
    print("\nTesting 3 sample prompts...")
    
    # Initialize service
    print("\nInitializing Video Generation Service...")
    try:
        video_service = VideoGenerationService()
        if not video_service.veo_client:
            print("✗ Google Veo not available. Check API key in .env file")
            return
        print("✓ Service initialized\n")
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        return
    
    # Test first 3 templates
    results = []
    for i, template in enumerate(TEST_PROMPTS[:3]):
        result = await test_single_template(video_service, template, i)
        results.append(result)
        
        if i < 2:
            print("\nWaiting 5 seconds...")
            await asyncio.sleep(5)
    
    # Summary
    print("\n" + "="*80)
    print("QUICK TEST SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r["success"]]
    print(f"\n✓ Generated {len(successful)}/3 videos")
    
    if successful:
        for r in successful:
            print(f"  - {r['name']}: {r['size_mb']:.2f} MB")
        print(f"\nLocation: {settings.VIDEOS_DIR}")
    
    print("\n" + "="*80 + "\n")


def main():
    """Main test runner"""
    
    print("\n" + "="*80)
    print("VEO 3.1 TEMPLATE TEST SUITE")
    print("="*80)
    print("\nChoose test mode:")
    print("1. Quick Test (3 samples - ~3-5 minutes)")
    print("2. Full Test (all 6 templates - ~8-12 minutes)")
    print("3. Custom prompt")
    
    choice = input("\nEnter choice (1/2/3) [default: 1]: ").strip() or "1"
    
    if choice == "1":
        asyncio.run(test_quick_samples())
    elif choice == "2":
        confirm = input("\nThis will take 8-12 minutes. Continue? (y/n): ").strip().lower()
        if confirm == 'y':
            asyncio.run(test_all_templates())
        else:
            print("Test cancelled.")
    elif choice == "3":
        print("\nEnter your custom prompt:")
        custom_prompt = input("> ").strip()
        if custom_prompt:
            custom_template = {
                "name": "Custom",
                "prompt": custom_prompt,
                "duration": 5
            }
            
            async def test_custom():
                video_service = VideoGenerationService()
                if not video_service.veo_client:
                    print("✗ Google Veo not available")
                    return
                await test_single_template(video_service, custom_template, 0)
            
            asyncio.run(test_custom())
        else:
            print("No prompt provided.")
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
