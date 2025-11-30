"""
Helper Utilities
Common utility functions used across the application
"""
import hashlib
import re
import uuid
from pathlib import Path
from typing import Optional, Union, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def generate_unique_id(prefix: str = "") -> str:
    """
    Generate a unique ID
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        Unique ID string
    """
    unique_id = str(uuid.uuid4().hex[:12])
    return f"{prefix}{unique_id}" if prefix else unique_id


def generate_timestamp() -> str:
    """
    Generate timestamp string
    
    Returns:
        Timestamp in format YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitize filename to be filesystem-safe
    
    Args:
        filename: Original filename
        max_length: Maximum length
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Limit length
    if len(filename) > max_length:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        name = name[:max_length - len(ext) - 1]
        filename = f"{name}.{ext}" if ext else name
    
    return filename.strip('_')


def get_file_hash(file_path: Union[str, Path], algorithm: str = 'md5') -> str:
    """
    Calculate file hash
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (md5, sha256)
        
    Returns:
        Hash hexdigest
    """
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def get_text_hash(text: str, length: int = 8) -> str:
    """
    Get hash of text string
    
    Args:
        text: Text to hash
        length: Length of hash to return
        
    Returns:
        Hash string
    """
    hash_value = hashlib.md5(text.encode()).hexdigest()
    return hash_value[:length]


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """
    Get file size in MB
    
    Args:
        file_path: Path to file
        
    Returns:
        Size in megabytes
    """
    size_bytes = Path(file_path).stat().st_size
    return size_bytes / (1024 * 1024)


def split_text_into_chunks(
    text: str,
    max_length: int = 1000,
    separator: str = '\n'
) -> List[str]:
    """
    Split text into chunks
    
    Args:
        text: Text to split
        max_length: Maximum chunk length
        separator: Split separator
        
    Returns:
        List of text chunks
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for part in text.split(separator):
        part_length = len(part) + len(separator)
        
        if current_length + part_length > max_length and current_chunk:
            chunks.append(separator.join(current_chunk))
            current_chunk = [part]
            current_length = part_length
        else:
            current_chunk.append(part)
            current_length += part_length
    
    if current_chunk:
        chunks.append(separator.join(current_chunk))
    
    return chunks


def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    Extract keywords from text (simple version)
    
    Args:
        text: Text to analyze
        max_keywords: Maximum keywords to return
        
    Returns:
        List of keywords
    """
    # Remove common words
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
        'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
        'who', 'when', 'where', 'why', 'how'
    }
    
    # Extract words
    words = re.findall(r'\b[a-z]+\b', text.lower())
    
    # Filter stopwords and short words
    keywords = [w for w in words if w not in stopwords and len(w) > 3]
    
    # Count frequency
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    # Return top keywords
    return [word for word, freq in sorted_words[:max_keywords]]


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "1m 30s")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    
    if remaining_seconds == 0:
        return f"{minutes}m"
    
    return f"{minutes}m {remaining_seconds}s"


def validate_rhyme_text(text: str) -> tuple[bool, Optional[str]]:
    """
    Validate rhyme text input
    
    Args:
        text: Rhyme text to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Rhyme text cannot be empty"
    
    text = text.strip()
    
    if len(text) < 10:
        return False, "Rhyme text is too short (minimum 10 characters)"
    
    if len(text) > 2000:
        return False, "Rhyme text is too long (maximum 2000 characters)"
    
    # Check for minimum number of words
    words = text.split()
    if len(words) < 5:
        return False, "Rhyme text must contain at least 5 words"
    
    return True, None


def clean_json_string(json_str: str) -> str:
    """
    Clean JSON string from LLM response
    
    Args:
        json_str: Raw JSON string
        
    Returns:
        Cleaned JSON string
    """
    # Remove markdown code blocks
    json_str = re.sub(r'```json\s*', '', json_str)
    json_str = re.sub(r'```\s*', '', json_str)
    
    # Remove leading/trailing whitespace
    json_str = json_str.strip()
    
    # Fix common JSON issues
    json_str = json_str.replace('\n', ' ')
    json_str = re.sub(r'\s+', ' ', json_str)
    
    return json_str


def calculate_video_duration(scenes: List) -> float:
    """
    Calculate total video duration from scenes
    
    Args:
        scenes: List of Scene objects
        
    Returns:
        Total duration in seconds
    """
    return sum(scene.duration for scene in scenes)


def get_output_filename(
    base_name: str,
    prefix: str = "",
    suffix: str = "",
    extension: str = "mp4",
    add_timestamp: bool = True,
) -> str:
    """
    Generate output filename
    
    Args:
        base_name: Base filename
        prefix: Prefix to add
        suffix: Suffix to add
        extension: File extension
        add_timestamp: Whether to add timestamp
        
    Returns:
        Complete filename
    """
    base_name = sanitize_filename(base_name)
    
    parts = []
    if prefix:
        parts.append(prefix)
    parts.append(base_name)
    if suffix:
        parts.append(suffix)
    if add_timestamp:
        parts.append(generate_timestamp())
    
    filename = "_".join(parts)
    return f"{filename}.{extension}"


class ProgressTracker:
    """Simple progress tracker"""
    
    def __init__(self, total_steps: int, description: str = ""):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.start_time = datetime.now()
    
    def update(self, step: int = 1, message: str = ""):
        """Update progress"""
        self.current_step += step
        percentage = (self.current_step / self.total_steps) * 100
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        if self.current_step > 0:
            estimated_total = elapsed * (self.total_steps / self.current_step)
            remaining = estimated_total - elapsed
        else:
            remaining = 0
        
        logger.info(
            f"{self.description}: {self.current_step}/{self.total_steps} "
            f"({percentage:.1f}%) - {message} - "
            f"Remaining: {format_duration(remaining)}"
        )
    
    def complete(self):
        """Mark as complete"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        logger.info(
            f"{self.description}: Complete! "
            f"Total time: {format_duration(elapsed)}"
        )


# Example usage
if __name__ == "__main__":
    # Test utilities
    print("Testing utilities...")
    
    # Test ID generation
    print(f"Unique ID: {generate_unique_id('video_')}")
    print(f"Timestamp: {generate_timestamp()}")
    
    # Test filename sanitization
    filename = "My Video: Test/File.mp4"
    print(f"Sanitized: {sanitize_filename(filename)}")
    
    # Test text hash
    text = "Twinkle twinkle little star"
    print(f"Text hash: {get_text_hash(text)}")
    
    # Test keyword extraction
    keywords = extract_keywords(text)
    print(f"Keywords: {keywords}")
    
    # Test duration formatting
    print(f"Duration: {format_duration(125)}")
    
    # Test rhyme validation
    valid, error = validate_rhyme_text("Too short")
    print(f"Validation: {valid}, Error: {error}")
    
    valid, error = validate_rhyme_text("This is a longer rhyme text that should be valid")
    print(f"Validation: {valid}, Error: {error}")
    
    # Test progress tracker
    tracker = ProgressTracker(5, "Test Process")
    for i in range(5):
        tracker.update(message=f"Step {i+1}")
    tracker.complete()
