# 🎬 AI-Powered Children's Rhyme Video Generator

Transform children's rhymes into engaging, colorful videos using AI! This project uses FastAPI, LLMs (Gemini/OpenAI), Stable Diffusion, and MoviePy to create professional-looking videos from simple text input.

---

## ✨ Features

- 🤖 **AI Scene Generation**: Convert rhymes into visual scenes using LLMs
- 🎨 **Image Generation**: Create consistent, colorful images using Stable Diffusion
- 🎬 **Video Animation**: Animate images using LTX-Video (latest & fastest!)
- 🔊 **Voice Narration**: Add natural-sounding narration with gTTS
- 🎵 **Background Music**: Optional background music overlay
- 🖥️ **User-Friendly UI**: Interactive Gradio interface
- 🆓 **Free Tier Support**: Works with free APIs (Gemini + HuggingFace)
- ⚡ **Fast Generation**: LTX-Video provides quick, high-quality results

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- 8GB RAM (16GB recommended)
- 5GB free disk storage

### Installation

1. **Clone/Navigate to the project**
```powershell
cd "d:\YASH\AI Video generator\project 2.0"
```

2. **Create virtual environment**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Configure environment**
```powershell
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
notepad .env
```

### Get API Keys (Free!)

#### 1. Google Gemini API (Required)
- Visit: https://makersuite.google.com/app/apikey
- Sign in with Google account
- Click "Create API Key"
- Copy key to `.env` file: `GOOGLE_API_KEY=your_key_here`

#### 2. HuggingFace Token (Required)
- Visit: https://huggingface.co/settings/tokens
- Sign up/Login
- Click "New token" → "Read" access
- Copy token to `.env` file: `HUGGINGFACE_TOKEN=hf_your_token_here`

---

## 🎮 Usage

### Method 1: Gradio UI (Recommended)

```powershell
python run.py
```

Then open your browser to: `http://localhost:7860`

### Method 2: FastAPI Backend

```powershell
# Start server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# API docs available at: http://localhost:8000/docs
```

### Method 3: Direct API Call

```powershell
curl -X POST http://localhost:8000/api/generate-video `
  -H "Content-Type: application/json" `
  -d '{
    "rhyme_text": "Twinkle, twinkle, little star,\nHow I wonder what you are.",
    "num_scenes": 6,
    "video_mode": "animated",
    "style_preset": "children_book"
  }'
```

---

## 📖 Example Rhymes

Try these classic rhymes:

### 1. Twinkle Twinkle Little Star
```
Twinkle, twinkle, little star,
How I wonder what you are.
Up above the world so high,
Like a diamond in the sky.
```

### 2. Humpty Dumpty
```
Humpty Dumpty sat on a wall,
Humpty Dumpty had a great fall.
All the king's horses and all the king's men,
Couldn't put Humpty together again.
```

### 3. Mary Had a Little Lamb
```
Mary had a little lamb,
Its fleece was white as snow.
And everywhere that Mary went,
The lamb was sure to go.
```

---

## 🎨 Generation Modes

### Fast Mode (30-60 seconds)
- Static images with Ken Burns effects
- Quickest generation
- Great for testing

### Animated Mode (2-4 minutes) ⭐ DEFAULT
- Images animated with **LTX-Video** (Lightricks)
- Fast, high-quality video generation
- Best quality/speed balance
- Recommended for final videos

### Experimental Mode (5-10 minutes)
- Direct text-to-video generation
- Longer generation time
- Uses older models (ModelScope, etc.)

### Premium Mode (with paid API)
- Uses Runway ML or other premium APIs
- Highest quality
- Requires API credits

---

## 🎯 Project Structure

```
project 2.0/
├── app/
│   ├── config.py              # Configuration
│   ├── main.py                # FastAPI app
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── services/
│   │   ├── llm_service.py     # LLM integration
│   │   ├── image_service.py   # Image generation
│   │   ├── video_service.py   # Video generation
│   │   ├── audio_service.py   # Audio/TTS
│   │   └── video_editor.py    # Video assembly
│   ├── models/
│   │   └── schemas.py         # Data models
│   └── utils/
│       ├── helpers.py         # Utilities
│       └── prompt_templates.py
├── ui/
│   └── gradio_app.py          # Gradio interface
├── outputs/                   # Generated content
│   ├── scenes/
│   ├── audio/
│   └── videos/
├── tests/                     # Unit tests
├── .env                       # Your config
├── requirements.txt           # Dependencies
└── run.py                     # Entry point
```

---

## ⚙️ Configuration

Edit `.env` file to customize:

```env
# LLM Settings
DEFAULT_LLM=gemini              # gemini, openai
LLM_TEMPERATURE=0.7

# Video Settings
DEFAULT_VIDEO_MODE=animated     # fast, animated, experimental
VIDEO_RESOLUTION=512            # 512, 768, 1024
MAX_SCENES=8
SCENE_DURATION=5

# Style
DEFAULT_STYLE=children_book     # children_book, cartoon, watercolor, 3d
```

---

## 🧪 Testing

```powershell
# Run all tests
pytest tests/ -v

# Test specific service
pytest tests/test_llm_service.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 🐛 Troubleshooting

### "FFmpeg not found"
```powershell
pip install imageio-ffmpeg
# OR
choco install ffmpeg
```

### "API timeout"
- Reduce resolution: `VIDEO_RESOLUTION=512`
- Try different times (HF API is slower during peak hours)
- Check API keys are valid

### "Out of memory"
- Reduce number of scenes
- Lower resolution
- Process scenes sequentially

### "Invalid JSON from LLM"
- Check LLM temperature (try 0.5-0.7)
- Verify API key is correct
- Try different LLM provider

---

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

```
POST /api/generate-video          # Generate complete video
POST /api/generate-scenes         # LLM scene generation only
POST /api/generate-images         # Generate images only
POST /api/generate-audio          # Generate narration only
GET  /api/status/{job_id}         # Check job status
GET  /api/download/{video_id}     # Download video
GET  /health                      # Health check
```

---

## 🎓 Learning Resources

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Gradio Quickstart](https://gradio.app/quickstart/)
- [MoviePy Guide](https://zulko.github.io/moviepy/)
- [Stable Diffusion Guide](https://huggingface.co/docs/diffusers/)
- [Gemini API Docs](https://ai.google.dev/docs)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📝 License

This project is for educational purposes. Please respect API usage limits and terms of service.

---

## 🎯 Roadmap

- [x] Phase 1: Project structure
- [x] Phase 2: LLM integration
- [x] Phase 3: Image generation
- [x] Phase 4: Video generation
- [x] Phase 5: Audio/narration
- [x] Phase 6: Video assembly
- [x] Phase 7: FastAPI backend
- [x] Phase 8: Gradio UI
- [x] Phase 9: Testing
- [x] Phase 10: Documentation

---

## 💡 Tips

1. **Start with "Fast" mode** to test quickly
2. **Use consistent seeds** for reproducible results
3. **Keep rhymes short** (2-4 verses) for best results
4. **Try different styles** to find what works best
5. **Monitor API usage** to stay within free tiers

---

## 📞 Support

- **Documentation**: See `IMPLEMENTATION_GUIDE.md`
- **Issues**: Report bugs via GitHub Issues
- **Questions**: Check existing issues first

---

## 🌟 Acknowledgments

- **FastAPI** - Modern web framework
- **Gradio** - ML interface framework
- **Google Gemini** - LLM API
- **HuggingFace** - Model hosting
- **MoviePy** - Video editing
- **Stable Diffusion** - Image generation

---

**Built with ❤️ for educational purposes**

**Version**: 1.0.0  
**Last Updated**: October 29, 2025
