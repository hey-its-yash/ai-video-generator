"""
Main Entry Point
Launches the Gradio UI interface
"""
import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import after path is set
from app.config import settings, print_config_summary
from ui.gradio_app import create_gradio_interface


def main():
    """Main entry point"""
    print("\n")
    print("=" * 70)
    print("🎬 AI-Powered Children's Rhyme Video Generator".center(70))
    print("=" * 70)
    print("\n")
    
    # Print configuration
    print_config_summary()
    
    # Check API keys
    api_keys = settings.validate_api_keys()
    if not api_keys.get('gemini') and not api_keys.get('openai'):
        print("\n⚠️  WARNING: No LLM API keys configured!")
        print("   Please add GOOGLE_API_KEY or OPENAI_API_KEY to .env file")
        print("   Get Gemini key: https://makersuite.google.com/app/apikey")
        print("\n")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    if not api_keys.get('huggingface'):
        print("\n⚠️  WARNING: HuggingFace token not configured!")
        print("   Image/Video generation may not work properly")
        print("   Get token: https://huggingface.co/settings/tokens")
        print("\n")
    
    print("\n🚀 Starting Gradio interface...")
    print(f"📍 Server will run on: http://localhost:7860")
    print("   Press Ctrl+C to stop")
    print("\n")
    
    # Create and launch Gradio interface
    try:
        demo = create_gradio_interface()
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,  # Set to True to create public link
            show_error=True,
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
