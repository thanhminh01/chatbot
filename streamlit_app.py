import streamlit as st
import requests
import json
import base64
import io
from pydub import AudioSegment
import tempfile
import time

st.set_page_config(page_title="Voice to Text with AssemblyAI", page_icon="🎤")

st.title("Voice to Text Converter")
st.write("Record your voice and convert it to text using AssemblyAI")

# AssemblyAI API key input
api_key = st.text_input("Enter your AssemblyAI API key", type="password")

# Audio recorder
audio_bytes = st.audio_recorder(
    text="Click to record",
    recording_color="#e74c3c",
    neutral_color="#3498db",
    stop_recording_text="Click to stop recording",
)

# Function to transcribe audio using AssemblyAI
def transcribe_audio(audio_bytes, api_key):
    # Convert audio bytes to WAV format
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file.write(audio_bytes)
        temp_file_path = temp_file.name
    
    # Upload the audio file to AssemblyAI
    upload_endpoint = "https://api.assemblyai.com/v2/upload"
    headers = {
        "authorization": api_key,
        "content-type": "application/json"
    }
    
    with open(temp_file_path, "rb") as f:
        response = requests.post(
            upload_endpoint,
            headers=headers,
            data=f
        )
    
    if response.status_code != 200:
        return f"Error uploading audio: {response.text}"
    
    audio_url = response.json()["upload_url"]
    
    # Submit the audio file for transcription
    transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
    json_data = {
        "audio_url": audio_url
    }
    
    response = requests.post(
        transcript_endpoint,
        headers=headers,
        json=json_data
    )
    
    if response.status_code != 200:
        return f"Error submitting transcription: {response.text}"
    
    transcript_id = response.json()["id"]
    
    # Poll for transcription completion
    polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    
    while True:
        response = requests.get(polling_endpoint, headers=headers)
        status = response.json()["status"]
        
        if status == "completed":
            return response.json()["text"]
        elif status == "error":
            return f"Transcription error: {response.json()['error']}"
        
        st.write(f"Transcription status: {status}")
        st.spinner("Processing...")
        time.sleep(1)

# Process recorded audio
if audio_bytes and api_key:
    st.audio(audio_bytes, format="audio/wav")
    
    with st.spinner("Transcribing audio..."):
        try:
            transcription = transcribe_audio(audio_bytes, api_key)
            st.success("Transcription complete!")
            st.subheader("Transcription:")
            st.write(transcription)
        except Exception as e:
            st.error(f"Error during transcription: {str(e)}")
elif audio_bytes and not api_key:
    st.warning("Please enter your AssemblyAI API key to transcribe the audio.")

# Instructions
st.markdown("""
## How to use:
1. Enter your AssemblyAI API key (get one at [assemblyai.com](https://www.assemblyai.com/))
2. Click the record button and speak
3. Click again to stop recording
4. Wait for the transcription to complete
""")

# Requirements note
st.info("Note: This app requires the 'pydub' package. Install it with 'pip install pydub'.")
