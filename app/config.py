"""
Configuration Management
Loads environment variables and provides application settings
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application Settings"""
    
    # ================================
    # APP CONFIGURATION
    # ================================
    APP_NAME: str = "AI Rhyme Video Generator"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # ================================
    # API KEYS
    # ================================
    GOOGLE_API_KEY: Optional[str] = None
    HUGGINGFACE_TOKEN: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    REPLICATE_API_TOKEN: Optional[str] = None
    STABILITY_API_KEY: Optional[str] = None
    
    # ================================
    # LLM SETTINGS
    # ================================
    DEFAULT_LLM: str = "gemini"  # gemini, openai, huggingface
    LLM_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1500
    LLM_TIMEOUT: int = 60
    
    # ================================
    # VIDEO GENERATION SETTINGS
    # ================================
    DEFAULT_VIDEO_MODE: str = "animated"  # fast, animated, experimental, premium
    VIDEO_FPS: int = 24
    VIDEO_RESOLUTION: int = 512
    MAX_SCENES: int = 8
    SCENE_DURATION: int = 5
    VIDEO_FORMAT: str = "mp4"
    
    # ================================
    # IMAGE GENERATION SETTINGS
    # ================================
    IMAGE_MODEL: str = "stabilityai/stable-diffusion-2-1"
    IMAGE_GUIDANCE_SCALE: float = 7.5
    IMAGE_NUM_INFERENCE_STEPS: int = 30
    IMAGE_SEED: int = -1  # -1 for random
    
    # ================================
    # VIDEO GENERATION SETTINGS
    # ================================
    VIDEO_MODEL: str = "Lightricks/LTX-Video"
    VIDEO_MODEL_FALLBACK: str = "stabilityai/stable-video-diffusion-img2vid-xt"
    VIDEO_FRAMES: int = 14
    VIDEO_MOTION_BUCKET_ID: int = 127
    VIDEO_FPS_ID: int = 7
    VIDEO_DURATION: int = 5
    
    # ================================
    # AUDIO SETTINGS
    # ================================
    TTS_LANGUAGE: str = "en"
    TTS_ACCENT: str = "com"  # com=US, co.uk=UK, co.in=India
    TTS_SLOW: bool = False
    ENABLE_BACKGROUND_MUSIC: bool = True
    BACKGROUND_MUSIC_VOLUME: float = 0.2
    
    # ================================
    # FILE PATHS
    # ================================
    OUTPUT_DIR: Path = BASE_DIR / "outputs"
    SCENES_DIR: Path = BASE_DIR / "outputs" / "scenes"
    AUDIO_DIR: Path = BASE_DIR / "outputs" / "audio"
    VIDEOS_DIR: Path = BASE_DIR / "outputs" / "videos"
    TEMP_DIR: Path = BASE_DIR / "outputs" / "temp"
    ASSETS_DIR: Path = BASE_DIR / "assets"
    MUSIC_DIR: Path = BASE_DIR / "assets" / "music"
    EXAMPLES_DIR: Path = BASE_DIR / "assets" / "examples"
    
    # ================================
    # PERFORMANCE SETTINGS
    # ================================
    MAX_CONCURRENT_REQUESTS: int = 3
    REQUEST_TIMEOUT: int = 120
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 86400  # 24 hours
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 2
    
    # ================================
    # STYLE PRESETS
    # ================================
    DEFAULT_STYLE: str = "children_book"
    STYLE_CONSISTENCY_SEED: bool = True
    
    # ================================
    # SAFETY & LIMITS
    # ================================
    MAX_RHYME_LENGTH: int = 500
    MIN_SCENES: int = 3
    MAX_VIDEO_DURATION: int = 120
    MAX_FILE_SIZE_MB: int = 100
    
    # ================================
    # DEVELOPMENT
    # ================================
    LOG_LEVEL: str = "INFO"
    ENABLE_CORS: bool = True
    ALLOWED_ORIGINS: str = "*"
    
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields like HF_TOKEN
    )
    
    @field_validator("OUTPUT_DIR", "SCENES_DIR", "AUDIO_DIR", "VIDEOS_DIR", 
               "TEMP_DIR", "ASSETS_DIR", "MUSIC_DIR", "EXAMPLES_DIR")
    @classmethod
    def ensure_dir_exists(cls, v):
        """Ensure directories exist"""
        if v and not v.exists():
            v.mkdir(parents=True, exist_ok=True)
        return v
    
    def validate_api_keys(self) -> dict:
        """Check which API keys are configured"""
        return {
            "gemini": bool(self.GOOGLE_API_KEY),
            "openai": bool(self.OPENAI_API_KEY),
            "huggingface": bool(self.HUGGINGFACE_TOKEN),
            "replicate": bool(self.REPLICATE_API_TOKEN),
            "stability": bool(self.STABILITY_API_KEY),
        }
    
    def get_available_llms(self) -> list:
        """Get list of available LLM providers"""
        available = []
        if self.GOOGLE_API_KEY:
            available.append("gemini")
        if self.OPENAI_API_KEY:
            available.append("openai")
        if self.HUGGINGFACE_TOKEN:
            available.append("huggingface")
        return available
    
    def get_video_dimensions(self) -> tuple:
        """Get video dimensions based on resolution"""
        res = self.VIDEO_RESOLUTION
        return (res, res)  # Square format for now
    
    @property
    def style_presets(self) -> dict:
        """Available style presets"""
        return {
            "children_book": "children's book illustration, colorful, vibrant, whimsical",
            "cartoon": "cartoon style, animated, bold colors, playful",
            "watercolor": "watercolor painting, soft colors, dreamy, artistic",
            "3d": "3D rendered, Pixar style, smooth, professional",
            "anime": "anime style, manga art, expressive, detailed",
        }


# Create global settings instance
settings = Settings()


# Helper functions
def get_settings() -> Settings:
    """Get application settings"""
    return settings


def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        settings.OUTPUT_DIR,
        settings.SCENES_DIR,
        settings.AUDIO_DIR,
        settings.VIDEOS_DIR,
        settings.TEMP_DIR,
        settings.ASSETS_DIR,
        settings.MUSIC_DIR,
        settings.EXAMPLES_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def print_config_summary():
    """Print configuration summary"""
    print("=" * 60)
    print(f"🎬 {settings.APP_NAME}")
    print("=" * 60)
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"Default LLM: {settings.DEFAULT_LLM}")
    print(f"Video Mode: {settings.DEFAULT_VIDEO_MODE}")
    print(f"Resolution: {settings.VIDEO_RESOLUTION}x{settings.VIDEO_RESOLUTION}")
    print(f"Max Scenes: {settings.MAX_SCENES}")
    print("-" * 60)
    print("API Keys Configured:")
    for key, configured in settings.validate_api_keys().items():
        status = "✅" if configured else "❌"
        print(f"  {status} {key.capitalize()}")
    print("-" * 60)
    print(f"Output Directory: {settings.OUTPUT_DIR}")
    print("=" * 60)


# Initialize directories on import
ensure_directories()


if __name__ == "__main__":
    # Test configuration
    print_config_summary()
    print("\nAvailable LLMs:", settings.get_available_llms())
    print("Style Presets:", list(settings.style_presets.keys()))
