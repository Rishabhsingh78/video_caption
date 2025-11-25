# backend/app/renderer.py
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.config import change_settings

# Configure ImageMagick path for MoviePy (ImageMagick 7 uses 'magick' command)
IMAGEMAGICK_BINARY = "/opt/homebrew/bin/magick"
if os.path.exists(IMAGEMAGICK_BINARY):
    change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})
    print(f" ImageMagick configured: {IMAGEMAGICK_BINARY}")
else:
    # Fallback to 'convert' for older versions
    IMAGEMAGICK_BINARY = "/opt/homebrew/bin/convert"
    if os.path.exists(IMAGEMAGICK_BINARY):
        change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})
        print(f" ImageMagick configured: {IMAGEMAGICK_BINARY}")
    else:
        print(f"  ImageMagick not found")

# Helper: load fonts by path
def _font_path(fonts_dir, name):
    return os.path.join(fonts_dir, name)

def render_with_style(input_video_path, srt_path, output_path, style="bottom", fonts_dir=None):
    """
    style: 'bottom' | 'top' | 'karaoke'
    fonts_dir: path where NotoSans & NotoSansDevanagari ttf are stored
    """
    print(f"🎬 Starting render: {style} style")
    print(f"   Input: {input_video_path}")
    print(f"   SRT: {srt_path}")
    print(f"   Output: {output_path}")
    
    # Load video
    video = VideoFileClip(input_video_path)
    w, h = video.size
    print(f"   Video size: {w}x{h}, duration: {video.duration:.2f}s")

    # Create subtitles generator with support for mixed Hindi (Devanagari) and English
    def generator(txt):
        """
        Generate text clips that support both Devanagari (Hindi) and Latin (English) scripts.
        Uses Noto Sans fonts which have excellent Unicode coverage.
        """
        # Font priority list for mixed Hindi-English support
        # Use absolute path to ensure ImageMagick finds the font
        user_home = os.path.expanduser("~")
        font_priority = [
            "Arial-Unicode-MS",  # Best coverage for mixed English/Hindi on macOS
            f"{user_home}/Library/Fonts/NotoSansDevanagari-Regular.ttf",  # Absolute path
            "Noto-Sans-Devanagari",
            "NotoSansDevanagari-Regular",
            "Noto-Sans",
            "Arial"
        ]
        
        # Try each font in priority order
        for font in font_priority:
            try:
                # Check if file exists if it's a path
                if "/" in font and not os.path.exists(font):
                    continue
                    
                txt_clip = TextClip(
                    txt, 
                    font=font, 
                    fontsize=52,  # Larger for better readability
                    color='white', 
                    stroke_color='black', 
                    stroke_width=2.5,  # Thicker stroke for better contrast
                    method='label',
                    kerning=0  # Adjust letter spacing if needed
                )
                print(f"    Using font: {font}")
                return txt_clip
            except Exception as e:
                print(f"     Font '{font}' failed: {str(e)[:50]}...")
                continue
        
        # Ultimate fallback: simple text without stroke
        print(f"    All fonts failed, using basic Arial without stroke")
        try:
            txt_clip = TextClip(
                txt,
                font='Arial',
                fontsize=52,
                color='white',
                method='label'
            )
            return txt_clip
        except Exception as e:
            print(f"    Critical error: {e}")
            raise RuntimeError(f"Failed to create text clip: {e}")

    # Create SubtitlesClip (uses pysrt-like srt)
    print("   Creating subtitle clips...")
    subs = SubtitlesClip(srt_path, generator)

    # Style presets: position the subtitles clip accordingly
    if style == "bottom":
        subs = subs.set_position(("center", h - 100))
    elif style == "top":
        subs = subs.set_position(("center", 20))
    elif style == "karaoke":
        # For karaoke-like effect: create plain subtitles then overlay a translucent highlight clip.
        # MoviePy does not support word-level time by default from SRT, so we animate an expanding mask over each subtitle.
        # Simplest approach: render subtitles at center and use a semi-transparent bar behind text.
        subs = subs.set_position(("center", h - 150))
    else:
        subs = subs.set_position(("center", h - 100))

    print("   Compositing video with subtitles...")
    final = CompositeVideoClip([video, subs.set_duration(video.duration)])
    
    # Write file with ffmpeg
    print("   Encoding final video (this may take a while)...")
    final.write_videofile(output_path, codec="libx264", audio_codec="aac", threads=4, fps=video.fps)

    # Close clips
    final.close()
    video.close()
    subs.close()
    
    print(f" Render complete: {output_path}")
