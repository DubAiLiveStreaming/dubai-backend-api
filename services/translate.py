from deep_translator import GoogleTranslator

translator = GoogleTranslator(source="auto", target="ta")

def translate_segments(segments: list) -> list:
    translated = []
    for seg in segments:
        try:
            tamil_text = translator.translate(seg["text"].strip())
        except Exception:
            tamil_text = seg["text"]
        translated.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": tamil_text
        })
    return translated