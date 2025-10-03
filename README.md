

# 🗣️ AI-Powered Speech Transcription, Translation & Accent Conversion

 
AI-powered web app for **speech transcription, multi-language translation, accent conversion, and reading text in different languages**. Upload or record audio and listen in various accents or translated voices.

---

## Overview

This project is a **Streamlit application** that demonstrates **end-to-end AI speech processing**. Users can **upload audio files** or **record their voice**, and the app performs the following tasks:

- **Noise Reduction:** Removes background noise from the audio using `librosa` and `noisereduce`.
- **Speech-to-Text Transcription:** Converts spoken audio into text using **AssemblyAI**.
- **Translation:** Translates the transcribed text into multiple languages (English, Hindi, Telugu, French, Spanish, German) using free translation APIs.
- **Accent Conversion:** Converts text-to-speech in **selected English accents** (British, American, Australian, Indian) using **Google Cloud TTS**.
- **Read Translated Text:** Speaks the translated text in the **native language voice**, allowing users to hear the text in different accents or languages.

---

## Features
- Supports both **audio file uploads** and **live voice recording**.
- Provides **step-wise progress feedback** for transcription, translation, and accent conversion.
- Allows users to **listen to results in different accents or translated languages**.
- Free and easy to run locally, no heavy models required.

---

## Tech Stack
- **Python**, **Streamlit**  
- **AssemblyAI API** for transcription  
- **Google Cloud Text-to-Speech** for accent conversion and reading translated text  
- **librosa** and **noisereduce** for audio preprocessing  

---

## How to Run
1. Clone the repo: git clone <your-repo-url>
   

2.Install dependencies: pip install -r requirements.txt
  

3.Set up environment variables (.env) and Google Cloud TTS credentials.

4.Run the app: streamlit run app.py
