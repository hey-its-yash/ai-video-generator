"""
Gradio Web Interface for AI Video Generator
Main UI for converting children's rhymes into videos
"""
import sys
import asyncio
import logging
import time
from pathlib import Path

import gradio as gr

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.services.llm_service import LLMService
from app.services.audio_service import AudioService
from app.services.video_service import VideoGenerationService
from app.services.video_editor import VideoEditorService
from app.utils.helpers import generate_unique_id, generate_timestamp

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoGeneratorPipeline:
    """Main pipeline for generating videos from rhymes"""
    
    def __init__(self):
        self.llm_service = None
        self.audio_service = None
        self.video_service = None
        self.editor_service = None
        self._initialized = False
    
    def initialize(self):
        """Initialize all services"""
        if self._initialized:
            return
        
        logger.info("Initializing services...")
        self.llm_service = LLMService()
        self.audio_service = AudioService()
        self.video_service = VideoGenerationService()
        self.editor_service = VideoEditorService()
        self._initialized = True
        logger.info("All services initialized!")
    
    async def generate_video(
        self,
        rhyme_text: str,
        num_scenes: int = 6,
        style: str = "children_book",
        progress_callback=None
    ):
        """
        Main pipeline: Rhyme → Scenes → Videos + Audio → Final Video
        """
        self.initialize()
        
        job_id = f"video_{generate_timestamp()}_{generate_unique_id()[:6]}"
        logger.info(f"Starting job: {job_id}")
        
        def update_progress(message, progress_value):
            if progress_callback:
                progress_callback(progress_value, desc=message)
            logger.info(f"[{progress_value:.0%}] {message}")
        
        try:
            # ============================================
            # STEP 1: Generate Scenes from Rhyme (LLM)
            # ============================================
            update_progress("🎬 Generating scenes from rhyme...", 0.1)
            
            scene_result = await self.llm_service.generate_scenes(
                rhyme_text=rhyme_text,
                num_scenes=num_scenes,
                style=style
            )
            
            scenes = scene_result.scenes
            total_scenes = len(scenes)
            logger.info(f"Generated {total_scenes} scenes")
            
            update_progress(f"✅ Generated {total_scenes} scenes", 0.2)
            
            # ============================================
            # STEP 2: Generate Video + Audio for each scene
            # ============================================
            for i, scene in enumerate(scenes):
                scene_progress_base = 0.2 + (0.6 * (i / total_scenes))
                scene_num = scene.scene_number
                
                # --- Generate Audio (TTS) ---
                update_progress(f"🔊 Scene {scene_num}/{total_scenes}: Generating audio...", scene_progress_base)
                
                try:
                    audio_filename = f"{job_id}_scene_{scene_num}"
                    audio_path = await self.audio_service.generate_narration(
                        text=scene.narration,
                        filename=audio_filename
                    )
                    scene.audio_path = str(audio_path)
                    
                    # Get audio duration
                    audio_duration = await self.audio_service.get_audio_duration(audio_path)
                    scene.duration = max(audio_duration, 3.0)  # Minimum 3 seconds
                    logger.info(f"Scene {scene_num} audio: {audio_duration:.1f}s")
                    
                except Exception as e:
                    logger.error(f"Audio generation failed for scene {scene_num}: {e}")
                    scene.duration = 5.0  # Default duration
                
                # --- Generate Video (Text-to-Video) ---
                update_progress(f"🎥 Scene {scene_num}/{total_scenes}: Generating video...", scene_progress_base + 0.03)
                
                try:
                    # Add delay between API calls to respect rate limits
                    if i > 0:
                        await asyncio.sleep(3)
                    
                    video_bytes = await self.video_service.generate_video_from_text(
                        prompt=scene.description,
                        duration=int(scene.duration) + 1,
                        model="veo"
                    )
                    
                    # Save video file
                    video_filename = f"{job_id}_scene_{scene_num}.mp4"
                    video_path = settings.TEMP_DIR / video_filename
                    
                    with open(video_path, "wb") as f:
                        f.write(video_bytes)
                    
                    scene.video_path = str(video_path)
                    logger.info(f"Scene {scene_num} video saved: {video_filename}")
                    
                except Exception as e:
                    logger.error(f"Video generation failed for scene {scene_num}: {e}")
                    # Create fallback color clip
                    await self._create_fallback_video(scene, job_id)
            
            # ============================================
            # STEP 3: Assemble Final Video
            # ============================================
            update_progress("🎞️ Assembling final video...", 0.85)
            
            output_filename = f"{scene_result.title.replace(' ', '_')}_{job_id}"
            
            final_path = self.editor_service.assemble_video(
                scenes=scenes,
                output_filename=output_filename
            )
            
            update_progress("✅ Video generation complete!", 1.0)
            
            return {
                "success": True,
                "video_path": str(final_path),
                "title": scene_result.title,
                "num_scenes": total_scenes,
                "duration": scene_result.total_duration,
                "job_id": job_id
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "job_id": job_id
            }
    
    async def _create_fallback_video(self, scene, job_id):
        """Create a simple fallback video when generation fails"""
        try:
            from moviepy.editor import ColorClip
            
            fallback_path = settings.TEMP_DIR / f"{job_id}_scene_{scene.scene_number}_fallback.mp4"
            clip = ColorClip(size=(512, 512), color=(100, 149, 237), duration=scene.duration)
            clip.write_videofile(str(fallback_path), fps=24, logger=None)
            clip.close()
            scene.video_path = str(fallback_path)
            logger.info(f"Created fallback video for scene {scene.scene_number}")
        except Exception as e:
            logger.error(f"Fallback video creation failed: {e}")


# Global pipeline instance
pipeline = VideoGeneratorPipeline()


def run_generation(rhyme_text, num_scenes, style, progress=gr.Progress()):
    """Wrapper function for Gradio to run async generation"""
    
    if not rhyme_text or len(rhyme_text.strip()) < 10:
        return None, "❌ Error: Please enter a rhyme with at least 10 characters."
    
    def progress_callback(value, desc=""):
        progress(value, desc=desc)
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            pipeline.generate_video(
                rhyme_text=rhyme_text,
                num_scenes=int(num_scenes),
                style=style,
                progress_callback=progress_callback
            )
        )
    finally:
        loop.close()
    
    if result["success"]:
        status = f"""
✅ **Video Generated Successfully!**

📌 **Title:** {result['title']}
🎬 **Scenes:** {result['num_scenes']}
⏱️ **Duration:** {result['duration']:.1f} seconds
📁 **File:** {result['video_path']}
🆔 **Job ID:** {result['job_id']}
"""
        return result["video_path"], status
    else:
        return None, f"❌ **Error:** {result.get('error', 'Unknown error occurred')}"


# Example rhymes for quick testing
EXAMPLE_RHYMES = {
    "Twinkle Twinkle": """Twinkle, twinkle, little star,
How I wonder what you are.
Up above the world so high,
Like a diamond in the sky.
Twinkle, twinkle, little star,
How I wonder what you are.""",

    "Humpty Dumpty": """Humpty Dumpty sat on a wall,
Humpty Dumpty had a great fall.
All the king's horses and all the king's men,
Couldn't put Humpty together again.""",

    "Mary Had a Little Lamb": """Mary had a little lamb,
Its fleece was white as snow.
And everywhere that Mary went,
The lamb was sure to go.""",

    "Jack and Jill": """Jack and Jill went up the hill,
To fetch a pail of water.
Jack fell down and broke his crown,
And Jill came tumbling after.""",

    "Baa Baa Black Sheep": """Baa, baa, black sheep,
Have you any wool?
Yes sir, yes sir,
Three bags full."""
}


def load_example(example_name):
    """Load an example rhyme"""
    return EXAMPLE_RHYMES.get(example_name, "")


def create_gradio_interface():
    """Create and return the Gradio interface"""
    
    with gr.Blocks(
        title="AI Rhyme Video Generator",
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="purple"),
        css="""
        .main-title { text-align: center; margin-bottom: 20px; }
        .generate-btn { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); }
        """
    ) as demo:
        
        # Header
        gr.Markdown(
            """
            # 🎬 AI-Powered Children's Rhyme Video Generator
            
            Transform children's rhymes into magical animated videos using AI!
            
            **Pipeline:** Rhyme Text → AI Scene Generation → Video Creation → Voice Narration → Final Video
            """,
            elem_classes=["main-title"]
        )
        
        with gr.Row():
            # Left Column - Input
            with gr.Column(scale=1):
                gr.Markdown("### 📝 Input")
                
                # Example dropdown
                example_dropdown = gr.Dropdown(
                    choices=list(EXAMPLE_RHYMES.keys()),
                    label="📚 Load Example Rhyme",
                    value=None,
                    interactive=True
                )
                
                # Main text input
                rhyme_input = gr.Textbox(
                    label="Enter Your Rhyme",
                    placeholder="Type or paste a children's rhyme here...\n\nExample:\nTwinkle, twinkle, little star,\nHow I wonder what you are.",
                    lines=8,
                    max_lines=15
                )
                
                # Settings
                with gr.Accordion("⚙️ Generation Settings", open=False):
                    num_scenes = gr.Slider(
                        minimum=3,
                        maximum=10,
                        value=6,
                        step=1,
                        label="Number of Scenes"
                    )
                    
                    style = gr.Dropdown(
                        choices=["children_book", "cartoon", "watercolor", "3d", "anime"],
                        value="children_book",
                        label="Visual Style"
                    )
                
                # Generate button
                generate_btn = gr.Button(
                    "🎬 Generate Video",
                    variant="primary",
                    size="lg",
                    elem_classes=["generate-btn"]
                )
            
            # Right Column - Output
            with gr.Column(scale=1):
                gr.Markdown("### 🎥 Output")
                
                # Video output
                video_output = gr.Video(
                    label="Generated Video",
                    height=400
                )
                
                # Status output
                status_output = gr.Markdown(
                    value="*Enter a rhyme and click Generate to create a video.*"
                )
        
        # Footer
        gr.Markdown(
            """
            ---
            **Tips:**
            - Start with short rhymes (4-8 lines) for best results
            - Each scene takes 1-2 minutes to generate
            - Total time: ~5-15 minutes depending on number of scenes
            
            **Requirements:** Google Gemini API key + HuggingFace Token in `.env` file
            """
        )
        
        # Event handlers
        example_dropdown.change(
            fn=load_example,
            inputs=[example_dropdown],
            outputs=[rhyme_input]
        )
        
        generate_btn.click(
            fn=run_generation,
            inputs=[rhyme_input, num_scenes, style],
            outputs=[video_output, status_output]
        )
    
    return demo


# For direct execution
if __name__ == "__main__":
    demo = create_gradio_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
