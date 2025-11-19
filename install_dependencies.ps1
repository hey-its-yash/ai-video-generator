# Installation Script for AI Rhyme Video Generator
# Run this after activating virtual environment

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI Rhyme Video Generator - Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version
Write-Host "✓ $pythonVersion" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ pip upgraded" -ForegroundColor Green
Write-Host ""

# Install core dependencies
Write-Host "Installing core dependencies..." -ForegroundColor Yellow
Write-Host "  This may take 5-10 minutes..." -ForegroundColor Gray
Write-Host ""

# Install in stages for better progress tracking
$packages = @(
    @("FastAPI & Uvicorn", "fastapi uvicorn[standard] python-multipart"),
    @("Gradio UI", "gradio"),
    @("AI/ML APIs", "google-generativeai openai huggingface-hub"),
    @("Image Processing", "diffusers transformers accelerate pillow"),
    @("Video Processing", "moviepy imageio imageio-ffmpeg"),
    @("Audio", "gTTS pydub"),
    @("HTTP Clients", "httpx aiohttp aiofiles requests"),
    @("Configuration", "python-dotenv pydantic pydantic-settings"),
    @("Utilities", "tqdm tenacity python-slugify"),
    @("Testing", "pytest pytest-asyncio")
)

$total = $packages.Count
$current = 0

foreach ($package in $packages) {
    $current++
    $name = $package[0]
    $pkgs = $package[1]
    
    Write-Host "[$current/$total] Installing $name..." -ForegroundColor Cyan
    python -m pip install $pkgs --quiet
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $name installed" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to install $name" -ForegroundColor Red
    }
    Write-Host ""
}

# Verify installations
Write-Host "Verifying installations..." -ForegroundColor Yellow
$imports = @(
    "fastapi",
    "gradio", 
    "google.generativeai",
    "huggingface_hub",
    "PIL",
    "moviepy",
    "gtts"
)

$failed = @()
foreach ($module in $imports) {
    $result = python -c "import $module" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $module" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $module" -ForegroundColor Red
        $failed += $module
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($failed.Count -eq 0) {
    Write-Host "✓ All dependencies installed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Configure .env with your API keys" -ForegroundColor White
    Write-Host "2. Run: python test_ltx_video.py" -ForegroundColor White
    Write-Host "3. Run: python app/config.py" -ForegroundColor White
    Write-Host "4. Run: python run.py" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "✗ Some packages failed to install" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Failed packages:" -ForegroundColor Red
    foreach ($pkg in $failed) {
        Write-Host "  - $pkg" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Try installing manually:" -ForegroundColor Yellow
    Write-Host "pip install $($failed -join ' ')" -ForegroundColor White
    Write-Host ""
}
