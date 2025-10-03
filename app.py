import os
import time
import streamlit as st
import assemblyai as aai
from google.cloud import texttospeech
from dotenv import load_dotenv
from st_audiorec import st_audiorec  # 🎤 Streamlit audio recorder
import noisereduce as nr
import librosa
import soundfile as sf
import requests

# ----------------- Load environment variables -----------------
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_tts_key.json"
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

st.title("🗣️ AI-Powered Speech Transcription, Translation & Accent Conversion")

# ----------------- Noise Reduction -----------------
def denoise_audio(input_path, output_path="cleaned_audio.wav"):
    y, sr = librosa.load(input_path, sr=None)
    reduced_noise = nr.reduce_noise(y=y, sr=sr)
    sf.write(output_path, reduced_noise, sr)
    return output_path

# ----------------- Translation -----------------
def translate_text(text, target_lang="en"):
    if target_lang == "en":
        return text
    try:
        response = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text, "langpair": f"en|{target_lang}"}
        )
        if response.status_code == 200:
            return response.json()["responseData"]["translatedText"]
        else:
            return f"⚠️ Translation API error: {response.text}"
    except Exception as e:
        return f"⚠️ Translation failed: {e}"

# ----------------- Session State Init -----------------
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "last_method" not in st.session_state:
    st.session_state.last_method = None

# ----------------- Input Options -----------------
input_method = st.radio(
    "Choose input method:", 
    ["Upload Audio File", "Record Voice"], 
    horizontal=True
)

# Reset state if method changed
if st.session_state.last_method != input_method:
    st.session_state.translated_text = ""
    st.session_state.last_method = input_method

audio_bytes = None

if input_method == "Upload Audio File":
    uploaded_file = st.file_uploader("Upload a WAV/MP3 audio file", type=["wav", "mp3"])
    if uploaded_file:
        audio_bytes = uploaded_file.getvalue()
        st.audio(audio_bytes, format="audio/wav")

elif input_method == "Record Voice":
    st.info("🎤 Speak for a few seconds, then process.")
    audio_bytes = st_audiorec()

# ----------------- Process Audio -----------------
if audio_bytes:
    st.subheader("📝 Extracted Text")

    # Save audio temporarily
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_bytes)

    # ----------------- Step 1: Noise reduction -----------------
    start_time = time.time()
    with st.spinner("🔊 Reducing noise..."):
        cleaned_path = denoise_audio("temp_audio.wav")
    st.success(f"✅ Noise reduction completed in {time.time()-start_time:.2f}s")

    # ----------------- Step 2: Transcription -----------------
    start_time = time.time()
    with st.spinner("⏳ Transcribing speech to text..."):
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(cleaned_path)

    if transcript.status == aai.TranscriptStatus.completed:
        text = transcript.text
        st.success(f"✅ Transcription completed in {time.time()-start_time:.2f}s")
        st.write(text)

        # ----------------- Step 3: Translation -----------------
        st.subheader("🌍 Translate Transcribed Text")
        lang_map = {
            "English": "en",
            "French": "fr",
            "Spanish": "es",
            "German": "de",
            "Hindi": "hi",
            "Telugu": "te"
        }

        target_lang = st.selectbox("Select translation language", list(lang_map.keys()), index=0)

        if st.button("Translate"):
            start_time = time.time()
            with st.spinner(f"🌐 Translating to {target_lang}..."):
                st.session_state.translated_text = translate_text(text, lang_map[target_lang])
            st.success(f"✅ Translation completed in {time.time()-start_time:.2f}s")

        if st.session_state.translated_text:
            st.info(st.session_state.translated_text)

        # ----------------- Step 4: Accent Conversion -----------------
        st.subheader("🎶 Accent Conversion")
        accent = st.selectbox("Select target accent", ["British", "American", "Australian", "Indian"])

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Speak in Selected Accent"):
                start_time = time.time()
                with st.spinner("🎤 Converting to selected accent..."):
                    client = texttospeech.TextToSpeechClient()
                    accent_map = {
                        "British": "en-GB-Standard-A",
                        "American": "en-US-Standard-C",
                        "Australian": "en-AU-Standard-B",
                        "Indian": "en-IN-Standard-A",
                    }
                    synthesis_input = texttospeech.SynthesisInput(text=st.session_state.translated_text)
                    voice = texttospeech.VoiceSelectionParams(
                        language_code=accent_map[accent].split("-")[0] + "-" + accent_map[accent].split("-")[1],
                        name=accent_map[accent]
                    )
                    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
                    response = client.synthesize_speech(
                        input=synthesis_input, voice=voice, audio_config=audio_config
                    )
                    output_file = "converted_accent.mp3"
                    with open(output_file, "wb") as out:
                        out.write(response.audio_content)
                st.success(f"✅ Accent Conversion completed in {time.time()-start_time:.2f}s")
                st.audio(output_file, format="audio/mp3")

        # ----------------- Step 5: Read Translated Text -----------------
        with col2:
            if st.button("Speak in Translated Language"):
                start_time = time.time()
                with st.spinner("📖 Reading translated text..."):
                    client = texttospeech.TextToSpeechClient()
                    lang_voice_map = {
                        "English": "en-US",
                        "French": "fr-FR",
                        "Spanish": "es-ES",
                        "German": "de-DE",
                        "Hindi": "hi-IN",
                        "Telugu": "te-IN"
                    }
                    synthesis_input = texttospeech.SynthesisInput(text=st.session_state.translated_text)
                    voice = texttospeech.VoiceSelectionParams(
                        language_code=lang_voice_map[target_lang],
                        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
                    )
                    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
                    response = client.synthesize_speech(
                        input=synthesis_input, voice=voice, audio_config=audio_config
                    )
                    output_file = f"translated_{target_lang}.mp3"
                    with open(output_file, "wb") as f:
                        f.write(response.audio_content)
                st.success(f"✅ Read Translated Text completed in {time.time()-start_time:.2f}s")
                st.audio(output_file, format="audio/mp3")

    else:
        st.error("❌ Transcription failed.")
