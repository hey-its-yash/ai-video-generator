"""
Generate Jack and Jill video
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from generate_video import VideoPipeline

poem = """Jack and Jill went up the hill
To fetch a pail of water;
Jack fell down and broke his crown,
And Jill came tumbling after."""

async def main():
    print("\n" + "="*60)
    print("🎬 Generating 'Jack and Jill' Video")
    print("="*60)
    print(f"\n📜 Poem:\n{poem}\n")
    
    pipeline = VideoPipeline()
    
    try:
        final_video = await pipeline.generate(
            poem_text=poem,
            num_scenes=4,
            style="children_book",
            output_name="jack_and_jill",
            parallel=True
        )
        print(f"\n\n🎉 SUCCESS! Video saved to: {final_video}")
        return final_video
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(main())
