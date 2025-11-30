"""
Test script for Audio Service
Tests gTTS integration and audio file handling
"""
import asyncio
import sys
from pathlib import Path
import logging

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.services.audio_service import AudioService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_audio_service():
    print("\n" + "="*80)
    print("AUDIO SERVICE TEST")
    print("="*80)
    
    # 1. Initialize Service
    print("\n1. Initializing Audio Service...")
    try:
        audio_service = AudioService()
        print("   ✓ Service initialized successfully")
    except Exception as e:
        print(f"   ✗ Failed to initialize service: {e}")
        return

    # 2. Test Generation
    print("\n2. Testing Narration Generation...")
    test_text = "Twinkle, twinkle, little star, How I wonder what you are!"
    test_filename = "test_twinkle"
    
    try:
        print(f"   Text: '{test_text}'")
        output_path = await audio_service.generate_narration(
            text=test_text,
            filename=test_filename
        )
        
        if output_path.exists():
            print(f"   ✓ Audio generated: {output_path}")
            print(f"   ✓ File size: {output_path.stat().st_size / 1024:.2f} KB")
        else:
            print("   ✗ File was not created")
            return
            
    except Exception as e:
        print(f"   ✗ Generation failed: {e}")
        return

    # 3. Test Duration
    print("\n3. Testing Duration Detection...")
    try:
        duration = await audio_service.get_audio_duration(output_path)
        print(f"   ✓ Duration: {duration:.2f} seconds")
        
        # Basic validation (should be > 0 and < 10 seconds for this short text)
        if 0 < duration < 10:
            print("   ✓ Duration seems reasonable")
        else:
            print("   ⚠ Duration seems unusual")
            
    except Exception as e:
        print(f"   ✗ Duration check failed: {e}")
        print("   (This might happen if ffmpeg is not installed/configured correctly)")

    print("\n" + "="*80)
    print("✓ Audio service test completed!")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_audio_service())
