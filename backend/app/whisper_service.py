# backend/app/whisper_service.py
import os
import ssl
from typing import List, Dict, Optional

# Fix SSL certificate issues on macOS
try:
    import certifi
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass

# Use OpenAI's Whisper instead of faster-whisper to avoid PyAV issues
model = None
error_message = None

try:
    import whisper
    print("Loading Whisper model (this may take a moment on first run)...")
    # Upgrade to 'small' model for better accuracy with Hindi/mixed languages
    # base (~139MB) -> small (~461MB)
    model = whisper.load_model("small")
    print(" Whisper model loaded successfully! (Model: small)")
except Exception as e:
    error_message = f"Whisper model failed to load: {str(e)}"
    print(f" ERROR: {error_message}")

def transcribe_local(path: str, language: Optional[str] = None) -> List[Dict]:
    """
    Transcribe audio from video file.
    
    Args:
        path: Path to video file
        language: Optional language code ('en', 'hi', 'es', etc.). 
                 If None, Whisper will auto-detect.
    
    Returns:
        List of segment dictionaries with start, end, and text
    """
    if model is None:
        raise RuntimeError(error_message or "Whisper model not loaded. Check server logs.")
    
    print(f"🎤 Transcribing: {path}")
    if language:
        print(f"   Language: {language}")
    else:
        print(f"   Language: auto-detect")
    
    # Transcribe with better parameters to prevent hallucinations
    result = model.transcribe(
        path,
        language=language,
        task='transcribe',
        temperature=0.0,
        best_of=5,
        beam_size=5,
        patience=1.0,
        # Hallucination prevention parameters:
        condition_on_previous_text=False,  # Prevents looping text like "No no no..."
        compression_ratio_threshold=2.4,   # Filters out repetitive text
        logprob_threshold=-1.0,           # Filters out low confidence text
        no_speech_threshold=0.6,          # Filters out silence/music
        word_timestamps=False,
        fp16=False,
    )
    
    segments = []
    detected_language = result.get('language', 'unknown')
    print(f"   Detected language: {detected_language}")
    
    for seg in result['segments']:
        segments.append({
            "start": seg['start'],
            "end": seg['end'],
            "text": seg['text'].strip()
        })
    
    print(f" Transcription complete: {len(segments)} segments")
    
    # Post-processing: Merge short segments for better pacing
    print(" Optimizing segments for better readability...")
    optimized_segments = merge_segments(segments)
    print(f" Optimization complete: {len(segments)} -> {len(optimized_segments)} segments")
    
    return optimized_segments

def merge_segments(segments: List[Dict], min_duration: float = 2.0, max_chars: int = 85) -> List[Dict]:
    """
    Merge short segments to prevent captions from moving too fast.
    
    Args:
        segments: List of segment dicts
        min_duration: Minimum duration for a segment (seconds)
        max_chars: Maximum characters per segment
    """
    if not segments:
        return []
        
    merged = []
    current = segments[0]
    
    for next_seg in segments[1:]:
        # Calculate gap between segments
        gap = next_seg['start'] - current['end']
        
        # Check if we should merge:
        # 1. Current segment is too short (time)
        # 2. OR Current segment is too short (text)
        # 3. AND Gap is small (part of same sentence)
        # 4. AND Merged text won't be too long
        
        is_short_time = (current['end'] - current['start']) < min_duration
        is_short_text = len(current['text']) < 30
        is_small_gap = gap < 1.0
        will_fit = (len(current['text']) + len(next_seg['text'])) < max_chars
        
        if (is_short_time or is_short_text) and is_small_gap and will_fit:
            # Merge logic
            current['end'] = next_seg['end']
            current['text'] += " " + next_seg['text']
        else:
            # Finalize current and start new
            merged.append(current)
            current = next_seg
            
    merged.append(current)
    return merged
