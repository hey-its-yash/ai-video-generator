"""
Test LLM Service
Test scene generation from rhymes using different LLM providers
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
import json
from app.services.llm_service import get_llm_service, generate_scenes_from_rhyme
from app.config import settings


async def test_llm_service():
    """Test LLM scene generation"""
    print("\n" + "=" * 70)
    print("🎬 Testing LLM Service - Scene Generation".center(70))
    print("=" * 70 + "\n")
    
    # Check configuration
    print("📋 Configuration Check:")
    print("-" * 70)
    
    api_keys = settings.validate_api_keys()
    for provider, configured in api_keys.items():
        status = "✅" if configured else "❌"
        print(f"  {status} {provider.capitalize()}")
    
    if not any([api_keys['gemini'], api_keys['openai'], api_keys['huggingface']]):
        print("\n❌ ERROR: No LLM providers configured!")
        print("   Please add at least one API key to .env:")
        print("   - GOOGLE_API_KEY (Gemini - Recommended & Free)")
        print("   - OPENAI_API_KEY (OpenAI - Paid)")
        print("   - HUGGINGFACE_TOKEN (HuggingFace - Free)")
        return False
    
    print()
    
    # Initialize service
    print("🔧 Initializing LLM Service...")
    service = get_llm_service()
    available_providers = service.get_available_providers()
    print(f"✅ Available providers: {', '.join(available_providers)}")
    print()
    
    # Test rhyme
    test_rhyme = """Twinkle, twinkle, little star,
How I wonder what you are.
Up above the world so high,
Like a diamond in the sky.
Twinkle, twinkle, little star,
How I wonder what you are."""
    
    print("📝 Test Rhyme:")
    print("-" * 70)
    print(test_rhyme)
    print("-" * 70)
    print()
    
    # Generate scenes
    print("🎨 Generating Scenes...")
    print("   This may take 10-30 seconds...")
    print()
    
    try:
        result = await generate_scenes_from_rhyme(
            rhyme_text=test_rhyme,
            num_scenes=6,
            style="children_book",
        )
        
        # Display results
        print("=" * 70)
        print("✅ SUCCESS! Scenes Generated".center(70))
        print("=" * 70)
        print()
        
        print(f"📌 Title: {result.title}")
        print(f"🎨 Style: {result.style[:80]}...")
        print(f"⏱️  Total Duration: {result.total_duration} seconds")
        print(f"🎬 Number of Scenes: {len(result.scenes)}")
        print()
        
        print("=" * 70)
        print("📋 Generated Scenes:")
        print("=" * 70)
        
        for i, scene in enumerate(result.scenes, 1):
            print(f"\n🎬 Scene {scene.scene_number}:")
            print(f"   Duration: {scene.duration}s")
            print(f"   Narration: {scene.narration}")
            print(f"   Description: {scene.description[:150]}...")
            print(f"   Keywords: {', '.join(scene.keywords)}")
        
        print()
        print("=" * 70)
        
        # Save to file
        output_file = settings.TEMP_DIR / "test_scenes.json"
        scenes_dict = {
            "title": result.title,
            "style": result.style,
            "total_duration": result.total_duration,
            "scenes": [
                {
                    "scene_number": s.scene_number,
                    "description": s.description,
                    "narration": s.narration,
                    "duration": s.duration,
                    "keywords": s.keywords,
                }
                for s in result.scenes
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(scenes_dict, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Scenes saved to: {output_file}")
        print()
        
        # Validation checks
        print("=" * 70)
        print("✓ Validation Checks:")
        print("=" * 70)
        
        checks = [
            ("Number of scenes", len(result.scenes) >= 3, f"{len(result.scenes)} scenes"),
            ("All scenes have descriptions", all(s.description for s in result.scenes), "✓"),
            ("All scenes have narration", all(s.narration for s in result.scenes), "✓"),
            ("Total duration > 0", result.total_duration > 0, f"{result.total_duration}s"),
            ("All scenes have keywords", all(s.keywords for s in result.scenes), "✓"),
        ]
        
        for check_name, passed, detail in checks:
            status = "✅" if passed else "❌"
            print(f"  {status} {check_name}: {detail}")
        
        print()
        print("=" * 70)
        print("🎉 LLM Service Test Complete!")
        print("=" * 70)
        print()
        
        print("Next steps:")
        print("1. ✅ LLM Service working")
        print("2. ⏳ Test Image Service (Stable Diffusion)")
        print("3. ⏳ Test Video Service (LTX-Video)")
        print("4. ⏳ Test Audio Service (gTTS)")
        print("5. ⏳ Combine everything into final video")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERROR: Scene generation failed")
        print("=" * 70)
        print(f"Error: {e}")
        print()
        
        import traceback
        traceback.print_exc()
        
        print()
        print("Troubleshooting:")
        print("1. Check API keys in .env are valid")
        print("2. Verify internet connection")
        print("3. Try a different LLM provider")
        print("4. Check API rate limits")
        print()
        
        return False


async def test_multiple_styles():
    """Test scene generation with different styles"""
    print("\n" + "=" * 70)
    print("🎨 Testing Different Visual Styles".center(70))
    print("=" * 70 + "\n")
    
    test_rhyme = "Humpty Dumpty sat on a wall, Humpty Dumpty had a great fall."
    
    styles = ["children_book", "cartoon", "watercolor", "3d"]
    
    for style in styles:
        print(f"\n📌 Testing style: {style}")
        print("-" * 70)
        
        try:
            result = await generate_scenes_from_rhyme(
                rhyme_text=test_rhyme,
                num_scenes=2,
                style=style,
            )
            
            print(f"✅ Generated {len(result.scenes)} scenes")
            print(f"   Style description: {result.style[:100]}...")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    print()


def main():
    """Main test function"""
    print("\n🚀 Starting LLM Service Tests\n")
    
    # Run main test
    success = asyncio.run(test_llm_service())
    
    if success:
        # Run additional tests
        response = input("\nTest different styles? (y/n): ")
        if response.lower() == 'y':
            asyncio.run(test_multiple_styles())
    
    print("\n✅ Testing complete!\n")


if __name__ == "__main__":
    main()
