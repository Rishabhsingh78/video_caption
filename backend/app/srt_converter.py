# backend/app/srt_converter.py
def format_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{ms:03}"

def segments_to_srt(segments):
    """
    segments: list of {start, end, text}
    returns SRT formatted string (utf-8)
    """
    s = ""
    for i, seg in enumerate(segments, start=1):
        s += f"{i}\n"
        s += f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n"
        s += seg['text'].replace('\n',' ') + "\n\n"
    return s
