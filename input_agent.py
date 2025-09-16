import speech_recognition as sr

def transcribe_audio_to_text(audio_file_path):
    """
    Transcribes speech from an audio file to text using Google's Speech Recognition API.

    Args:
        audio_file_path (str): Path to the audio file (supported formats: WAV, AIFF, FLAC).

    Returns:
        str: Transcribed text from the audio.
    """
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"