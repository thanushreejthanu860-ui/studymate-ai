import os
import hashlib
from gtts import gTTS

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "audio")


def text_to_mp3(text: str) -> str:
    """
    Convert text to an mp3 file saved in static/audio/.
    Returns the URL path like /static/audio/<filename>.mp3.
    Uses a hash of the text so the same text is never generated twice.
    """
    os.makedirs(AUDIO_DIR, exist_ok=True)
    name = hashlib.md5(text.encode()).hexdigest() + ".mp3"
    path = os.path.join(AUDIO_DIR, name)
    if not os.path.exists(path):
        tts = gTTS(text=text, lang="en")
        tts.save(path)
    return f"/static/audio/{name}"
