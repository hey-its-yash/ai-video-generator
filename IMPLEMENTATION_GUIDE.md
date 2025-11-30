# 🎬 AI-Powered Children's Rhyme Video Generator
## Implementation Guide & Instructions

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Setup Instructions](#setup-instructions)
5. [API Keys & Configuration](#api-keys--configuration)
6. [Development Phases](#development-phases)
7. [File Structure](#file-structure)
8. [Implementation Details](#implementation-details)
9. [Testing Strategy](#testing-strategy)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

### Goal
Build an AI-powered video generator that creates visually appealing, smooth, and logically consistent short videos from children's rhymes using free/freemium APIs.

### Key Features
- ✅ Text-to-Scene generation using LLMs (Gemini/OpenAI)
- ✅ Image generation using Stable Diffusion (HuggingFace)
- ✅ Image-to-Video using Stable Video Diffusion (HuggingFace)
- ✅ Voice narration using gTTS (free)
- ✅ Video assembly using MoviePy
- ✅ User-friendly Gradio interface
- ✅ Multiple generation modes (Fast/Animated/Experimental)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│                    (Gradio Web Interface)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   API Routes │  │  Validation  │  │    Config    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ LLM Service │  │Image Service│  │Audio Service│
│             │  │             │  │             │
│ • Gemini    │  │ • Stable    │  │ • gTTS      │
│ • OpenAI    │  │   Diffusion │  │ • Timing    │
│ • Fallbacks │  │ • HF API    │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
                ┌─────────────────┐
                │  Video Service  │
                │                 │
                │ • SVD (Img2Vid) │
                │ • Text-to-Video │
                │ • Fallbacks     │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Video Editor   │
                │                 │
                │ • MoviePy       │
                │ • Transitions   │
                │ • Audio Sync    │
                │ • Effects       │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Output Video   │
                │    (.mp4)       │
                └─────────────────┘
```

---

## 🛠️ Technology Stack

### Core Framework
- **Backend**: FastAPI 0.109.0
- **UI**: Gradio 4.19.0
- **Language**: Python 3.10+

### AI/ML Services
- **LLM**: 
  - Google Gemini 1.5 Flash (Primary - FREE)
  - OpenAI GPT-4o-mini (Fallback - Paid)
- **Image Generation**: 
  - Stable Diffusion via HuggingFace (FREE)
- **Video Generation**: 
  - Stable Video Diffusion (Image-to-Video) (FREE)
  - ModelScope/ZeroScope (Text-to-Video) (FREE)
- **Audio**: 
  - gTTS (Google Text-to-Speech) (FREE)

### Video Processing
- **Editor**: MoviePy 1.0.3
- **Codecs**: FFmpeg (auto-installed with MoviePy)

### Utilities
- **Environment**: python-dotenv
- **HTTP**: httpx, aiohttp
- **Image Processing**: Pillow
- **Progress**: tqdm

---

## 🚀 Setup Instructions

### Prerequisites
```bash
# Required
- Python 3.10 or higher
- pip (Python package manager)
- 8GB RAM minimum (16GB recommended)
- 5GB free disk space

# Optional
- CUDA-compatible GPU (for faster local processing)
- FFmpeg (auto-installed with MoviePy, but manual install recommended)
```

### Step 1: Clone/Navigate to Project
```bash
cd "d:\YASH\AI Video generator\project 2.0"
```

### Step 2: Create Virtual Environment
```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# If execution policy error occurs:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Install FFmpeg (Recommended)
```bash
# Option 1: Via Chocolatey (Windows)
choco install ffmpeg

# Option 2: Via pip (included with imageio-ffmpeg)
pip install imageio-ffmpeg

# Option 3: Manual download
# Download from: https://ffmpeg.org/download.html
# Add to PATH
```

### Step 5: Configure Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
notepad .env
```

### Step 6: Test Installation
```bash
python -c "import fastapi, gradio, moviepy; print('All core packages installed!')"
```

---

## 🔑 API Keys & Configuration

### Required API Keys

#### 1. **Google Gemini API** (PRIMARY - FREE)
```bash
# Get key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_gemini_api_key_here
```
- ✅ Free tier: 60 requests per minute
- ✅ No credit card required
- ✅ Best for students

#### 2. **HuggingFace Token** (FREE)
```bash
# Get token from: https://huggingface.co/settings/tokens
HUGGINGFACE_TOKEN=hf_your_token_here
```
- ✅ Free tier: Unlimited inference API calls
- ✅ Access to Stable Diffusion, SVD models
- ✅ No credit card required

### Optional API Keys

#### 3. **OpenAI API** (OPTIONAL - Paid Fallback)
```bash
OPENAI_API_KEY=sk-your_openai_key_here
```
- Used as fallback if Gemini fails
- Costs: ~$0.001-0.002 per request

#### 4. **Replicate API** (OPTIONAL - Better Performance)
```bash
REPLICATE_API_TOKEN=r8_your_token_here
```
- Alternative to HF for faster video generation
- Free $10 credits on signup

### Configuration Settings (.env)
```bash
# App Configuration
APP_NAME=AI Rhyme Video Generator
DEBUG=True
HOST=0.0.0.0
PORT=8000

# LLM Settings
DEFAULT_LLM=gemini              # Options: gemini, openai
LLM_TEMPERATURE=0.7
MAX_TOKENS=1000

# Video Generation Settings
DEFAULT_VIDEO_MODE=animated     # Options: fast, animated, experimental
VIDEO_FPS=24
VIDEO_RESOLUTION=512           # Options: 512, 768, 1024
MAX_SCENES=8
SCENE_DURATION=5               # seconds per scene

# Image Generation Settings
IMAGE_MODEL=stabilityai/stable-diffusion-2-1
IMAGE_GUIDANCE_SCALE=7.5
IMAGE_NUM_INFERENCE_STEPS=30

# Video Generation Settings
VIDEO_MODEL=stabilityai/stable-video-diffusion-img2vid-xt
VIDEO_FRAMES=14                # 14 frames = ~1-2 seconds at 7-14fps

# Audio Settings
TTS_LANGUAGE=en
TTS_ACCENT=com                 # com=US, co.uk=UK, co.in=India

# File Paths
OUTPUT_DIR=outputs
SCENES_DIR=outputs/scenes
AUDIO_DIR=outputs/audio
VIDEOS_DIR=outputs/videos
TEMP_DIR=outputs/temp

# Performance
MAX_CONCURRENT_REQUESTS=3
REQUEST_TIMEOUT=120            # seconds
ENABLE_CACHING=True
```

---

## 📦 Development Phases

### Phase 1: Foundation (Current) ✅
**Goal**: Setup project structure and core dependencies
- [x] Create directory structure
- [x] Setup requirements.txt
- [x] Create .env.example
- [x] Write implementation guide
- [ ] Create config.py
- [ ] Create base schemas

**Deliverable**: Working project skeleton

---

### Phase 2: LLM Integration 🔄
**Goal**: Scene generation from rhymes
- [ ] Implement Gemini API client
- [ ] Create prompt templates
- [ ] Build scene parser (JSON output)
- [ ] Add OpenAI fallback
- [ ] Test with sample rhymes

**Deliverable**: Working text-to-scene API endpoint

**Test Command**:
```bash
curl -X POST http://localhost:8000/api/generate-scenes \
  -H "Content-Type: application/json" \
  -d '{"rhyme": "Twinkle twinkle little star", "num_scenes": 6}'
```

---

### Phase 3: Image Generation 🔄
**Goal**: Create consistent scene images
- [ ] Implement HuggingFace Inference API client
- [ ] Add Stable Diffusion pipeline
- [ ] Style consistency logic
- [ ] Image caching system
- [ ] Error handling & retries

**Deliverable**: Working image generation endpoint

**Test Command**:
```bash
curl -X POST http://localhost:8000/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A bright star twinkling in the night sky, children book illustration style"}'
```

---

### Phase 4: Video Generation 🔄
**Goal**: Animate images using SVD
- [ ] Implement Stable Video Diffusion API
- [ ] Image-to-Video pipeline
- [ ] Text-to-Video (experimental)
- [ ] Progress tracking
- [ ] Fallback to static images

**Deliverable**: Working video generation from images

---

### Phase 5: Audio Generation 🔄
**Goal**: Add narration and timing
- [ ] Implement gTTS integration
- [ ] Calculate timing from text
- [ ] Sync with scene duration
- [ ] Background music overlay (optional)

**Deliverable**: Working audio generation

---

### Phase 6: Video Assembly 🔄
**Goal**: Combine everything into final video
- [ ] MoviePy video concatenation
- [ ] Audio overlay
- [ ] Scene transitions
- [ ] Ken Burns effects (zoom/pan)
- [ ] Export optimization

**Deliverable**: Complete video pipeline

---

### Phase 7: FastAPI Backend 🔄
**Goal**: RESTful API for all operations
- [ ] Create API routes
- [ ] Request validation
- [ ] Progress tracking endpoint
- [ ] File upload/download
- [ ] Error responses

**Deliverable**: Working REST API

**Endpoints**:
```
POST /api/generate-video          # Full pipeline
POST /api/generate-scenes         # LLM only
POST /api/generate-images         # Images only
POST /api/generate-audio          # Audio only
GET  /api/status/{job_id}         # Check progress
GET  /api/download/{video_id}     # Download video
```

---

### Phase 8: Gradio UI 🔄
**Goal**: User-friendly interface
- [ ] Input form (rhyme text)
- [ ] Model selection dropdowns
- [ ] Generation mode selector
- [ ] Progress bar
- [ ] Video preview
- [ ] Download button

**Deliverable**: Working web interface

---

### Phase 9: Testing & Optimization 🔄
**Goal**: Ensure reliability
- [ ] Unit tests for services
- [ ] Integration tests
- [ ] Load testing
- [ ] Performance optimization
- [ ] Error handling improvements

---

### Phase 10: Documentation & Deployment 🔄
**Goal**: Production-ready
- [ ] Complete README.md
- [ ] API documentation
- [ ] Usage examples
- [ ] Deployment guide
- [ ] Demo video

---

## 📁 File Structure

```
project 2.0/
│
├── 📄 IMPLEMENTATION_GUIDE.md      # This file
├── 📄 README.md                    # User documentation
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment template
├── 📄 .env                         # Actual config (gitignored)
├── 📄 .gitignore                   # Git ignore rules
├── 📄 run.py                       # Application entry point
│
├── 📁 app/                         # Main application
│   ├── 📄 __init__.py
│   ├── 📄 main.py                  # FastAPI application
│   ├── 📄 config.py                # Configuration loader
│   │
│   ├── 📁 api/                     # API routes
│   │   ├── 📄 __init__.py
│   │   ├── 📄 routes.py            # Main routes
│   │   └── 📄 websocket.py         # WebSocket for progress
│   │
│   ├── 📁 services/                # Business logic
│   │   ├── 📄 __init__.py
│   │   ├── 📄 llm_service.py       # LLM integrations
│   │   ├── 📄 image_service.py     # Image generation
│   │   ├── 📄 video_service.py     # Video generation
│   │   ├── 📄 audio_service.py     # TTS & audio
│   │   └── 📄 video_editor.py      # MoviePy assembly
│   │
│   ├── 📁 models/                  # Data models
│   │   ├── 📄 __init__.py
│   │   └── 📄 schemas.py           # Pydantic models
│   │
│   └── 📁 utils/                   # Utilities
│       ├── 📄 __init__.py
│       ├── 📄 helpers.py           # Helper functions
│       ├── 📄 validators.py        # Input validation
│       ├── 📄 prompt_templates.py  # LLM prompts
│       └── 📄 cache.py             # Caching logic
│
├── 📁 ui/                          # User interface
│   ├── 📄 __init__.py
│   └── 📄 gradio_app.py            # Gradio interface
│
├── 📁 outputs/                     # Generated content
│   ├── 📁 scenes/                  # Scene images
│   ├── 📁 audio/                   # Audio files
│   ├── 📁 videos/                  # Final videos
│   └── 📁 temp/                    # Temporary files
│
├── 📁 assets/                      # Static resources
│   ├── 📁 music/                   # Background music
│   ├── 📁 examples/                # Example rhymes
│   └── 📁 styles/                  # Style presets
│
└── 📁 tests/                       # Test files
    ├── 📄 __init__.py
    ├── 📄 test_llm_service.py
    ├── 📄 test_image_service.py
    ├── 📄 test_video_service.py
    └── 📄 test_integration.py
```

---

## 🔧 Implementation Details

### 1. LLM Service (llm_service.py)

**Purpose**: Convert rhyme text into structured scene descriptions

**Key Functions**:
```python
async def generate_scenes(rhyme_text: str, num_scenes: int = 6) -> List[Scene]
    """
    Uses LLM to break down rhyme into visual scenes
    Returns: List of Scene objects with descriptions, duration, narration
    """

async def generate_with_gemini(prompt: str) -> dict
    """Primary LLM - Gemini 1.5 Flash"""

async def generate_with_openai(prompt: str) -> dict
    """Fallback LLM - OpenAI GPT-4o-mini"""
```

**Prompt Strategy**:
```python
SCENE_GENERATION_PROMPT = """
You are a creative director for children's content. 
Convert this rhyme into {num_scenes} visual scenes perfect for a children's video.

Requirements:
1. Each scene should be 5 seconds long
2. Descriptions should be visual, colorful, and child-friendly
3. Maintain consistent style and characters across scenes
4. Include specific actions/movements
5. Output MUST be valid JSON

Rhyme:
{rhyme_text}

Output Format:
{{
  "title": "Rhyme title",
  "style": "children's book illustration, colorful, cartoon",
  "scenes": [
    {{
      "scene_number": 1,
      "description": "Detailed visual description for image generation",
      "narration": "Text to be spoken",
      "duration": 5,
      "keywords": ["keyword1", "keyword2"]
    }}
  ]
}}
"""
```

---

### 2. Image Service (image_service.py)

**Purpose**: Generate consistent images for each scene

**Key Functions**:
```python
async def generate_image_sd(prompt: str, style: str) -> bytes
    """
    Generate image using Stable Diffusion via HuggingFace API
    Returns: Image bytes
    """

async def ensure_consistency(prompts: List[str], style: str) -> List[bytes]
    """
    Generate multiple images with consistent style
    Uses same seed and style prefix
    """
```

**Consistency Strategy**:
```python
# Add style prefix to all prompts
style_prefix = "children's book illustration, colorful, cartoon style, "
full_prompt = f"{style_prefix}{scene_description}, consistent character design"

# Use same seed for all scenes
seed = hash(rhyme_text) % 1000000
```

---

### 3. Video Service (video_service.py)

**Purpose**: Convert images to video clips

**Key Functions**:
```python
async def generate_video_from_image(image_bytes: bytes) -> bytes
    """
    Animate image using Stable Video Diffusion
    Returns: Video clip bytes (2-3 seconds)
    """

async def generate_video_from_text(prompt: str) -> bytes
    """
    Generate video directly from text using ModelScope/ZeroScope
    Returns: Video clip bytes
    """
```

**Generation Modes**:
- **Fast**: Static images with Ken Burns effects
- **Animated** (Default): Images → SVD → Video clips
- **Experimental**: Direct text-to-video
- **Premium**: Runway ML (if API key available)

---

### 4. Audio Service (audio_service.py)

**Purpose**: Generate narration and time audio

**Key Functions**:
```python
async def generate_narration(text: str, language: str = 'en') -> tuple[bytes, float]
    """
    Generate speech using gTTS
    Returns: (audio_bytes, duration_seconds)
    """

def calculate_scene_timing(narration_duration: float, target_duration: float) -> dict
    """
    Adjust scene timing based on narration length
    """
```

---

### 5. Video Editor (video_editor.py)

**Purpose**: Assemble final video

**Key Functions**:
```python
async def create_video(scenes: List[VideoClip], audio: AudioClip) -> str
    """
    Main assembly function:
    1. Concatenate video clips
    2. Add transitions
    3. Overlay audio
    4. Add background music
    5. Export as MP4
    """

def add_ken_burns_effect(image_path: str, duration: float) -> VideoClip
    """
    Add zoom/pan animation to static images
    """
```

---

## 🧪 Testing Strategy

### Unit Tests
```bash
# Test individual services
pytest tests/test_llm_service.py -v
pytest tests/test_image_service.py -v
pytest tests/test_video_service.py -v
```

### Integration Tests
```bash
# Test full pipeline
pytest tests/test_integration.py -v
```

### Manual Testing
```bash
# Test with sample rhyme
python -c "
from app.services.llm_service import generate_scenes
result = generate_scenes('Twinkle twinkle little star')
print(result)
"
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. **FFmpeg Not Found**
```bash
Error: MoviePy requires FFmpeg

Solution:
pip install imageio-ffmpeg
# OR
choco install ffmpeg
```

#### 2. **HuggingFace API Timeout**
```bash
Error: Request timeout after 60 seconds

Solution:
- Use smaller models
- Reduce image resolution (512 instead of 1024)
- Try during off-peak hours
- Consider using Replicate API instead
```

#### 3. **Out of Memory**
```bash
Error: RuntimeError: CUDA out of memory

Solution:
- Reduce batch size
- Lower image resolution
- Use CPU instead of GPU
- Process scenes sequentially instead of parallel
```

#### 4. **API Rate Limits**
```bash
Error: 429 Too Many Requests

Solution:
- Add retry logic with exponential backoff
- Use multiple API keys (rotate)
- Implement request queuing
```

#### 5. **Invalid JSON from LLM**
```bash
Error: JSONDecodeError

Solution:
- Add JSON validation
- Use regex to extract JSON from response
- Add retry with improved prompt
- Fallback to structured output parsing
```

---

## 📚 Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Gradio Docs](https://gradio.app/docs/)
- [MoviePy Docs](https://zulko.github.io/moviepy/)
- [HuggingFace Inference API](https://huggingface.co/docs/api-inference/)
- [Gemini API Docs](https://ai.google.dev/docs)

### Models
- [Stable Diffusion Models](https://huggingface.co/models?pipeline_tag=text-to-image)
- [Stable Video Diffusion](https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt)
- [ModelScope Text-to-Video](https://huggingface.co/damo-vilab/text-to-video-ms-1.7b)

### Example Rhymes
```
1. Twinkle Twinkle Little Star
2. Humpty Dumpty
3. Jack and Jill
4. Baa Baa Black Sheep
5. Mary Had a Little Lamb
```

---

## 🎯 Success Criteria

The project is successful when:
- ✅ User can input any children's rhyme
- ✅ System generates 6-8 consistent visual scenes
- ✅ Video output is smooth and visually appealing
- ✅ Audio narration is synced correctly
- ✅ Total generation time < 5 minutes for 30-second video
- ✅ Works entirely on free tier APIs
- ✅ Simple, intuitive UI
- ✅ Ready for demo/presentation

---

## 📅 Timeline

- **Week 1**: Phases 1-3 (Foundation, LLM, Images)
- **Week 2**: Phases 4-6 (Video, Audio, Assembly)
- **Week 3**: Phases 7-8 (API, UI)
- **Week 4**: Phases 9-10 (Testing, Documentation)

---

## 🎓 Learning Objectives Achieved

By completing this project, students will learn:
1. ✅ Building production-ready REST APIs with FastAPI
2. ✅ Integrating multiple AI/ML APIs
3. ✅ Async programming in Python
4. ✅ Video processing with MoviePy
5. ✅ Prompt engineering for LLMs
6. ✅ Building user interfaces with Gradio
7. ✅ Error handling and fallback strategies
8. ✅ Environment configuration and secrets management
9. ✅ Testing strategies for AI applications
10. ✅ End-to-end product development

---

## 📝 Notes

- All API keys should be kept in `.env` file (never commit to git)
- Start with small test rhymes (2-3 lines)
- Test each service independently before integration
- Use caching to avoid redundant API calls
- Monitor API usage to stay within free tiers
- Keep video resolution at 512px for faster generation
- Use progress bars for long operations

---

**Version**: 1.0  
**Last Updated**: October 29, 2025  
**Author**: AI Video Generator Team  
**Status**: Phase 1 - Foundation ✅

---

## 🚀 Quick Start Commands

```bash
# Setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env

# Configure .env with your API keys
notepad .env

# Run FastAPI server
python run.py

# Run Gradio UI (in separate terminal)
python ui/gradio_app.py

# Run tests
pytest tests/ -v

# Generate sample video
curl -X POST http://localhost:8000/api/generate-video \
  -H "Content-Type: application/json" \
  -d @examples/twinkle_twinkle.json
```

---

**Ready to start implementation! 🎉**
