import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
import streamlit.components.v1 as components

# Load environment variables from .env file (if it exists)
load_dotenv()

st.set_page_config(
    page_title="Voice Recognition App", 
    page_icon="🎙️"
)

st.title("Simple Voice Recognition")
st.write("Click the microphone button and speak to see the transcription.")

# Voice input component using HTML/JavaScript
def voice_input():
    return components.html(
        """
        <script>
        const sendMessageToStreamlit = (message) => {
            window.parent.postMessage({type: "streamlit:setComponentValue", value: message}, "*");
        };

        // Function to handle speech recognition
        function setupSpeechRecognition() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();
                
                recognition.continuous = false;
                recognition.interimResults = true;
                recognition.lang = 'en-US';
                
                let finalTranscript = '';
                
                recognition.onstart = function() {
                    document.getElementById('status').textContent = 'Listening...';
                    document.getElementById('mic-btn').classList.add('recording');
                    sendMessageToStreamlit({status: "recording", transcript: ""});
                };
                
                recognition.onresult = function(event) {
                    let interimTranscript = '';
                    for (let i = event.resultIndex; i < event.results.length; ++i) {
                        if (event.results[i].isFinal) {
                            finalTranscript += event.results[i][0].transcript;
                        } else {
                            interimTranscript += event.results[i][0].transcript;
                        }
                    }
                    
                    document.getElementById('transcript').textContent = finalTranscript || interimTranscript;
                    
                    if (finalTranscript) {
                        sendMessageToStreamlit({status: "interim", transcript: finalTranscript});
                    }
                };
                
                recognition.onerror = function(event) {
                    document.getElementById('status').textContent = 'Error occurred: ' + event.error;
                    document.getElementById('mic-btn').classList.remove('recording');
                    sendMessageToStreamlit({status: "error", error: event.error});
                };
                
                recognition.onend = function() {
                    document.getElementById('status').textContent = 'Click to speak';
                    document.getElementById('mic-btn').classList.remove('recording');
                    
                    if (finalTranscript) {
                        sendMessageToStreamlit({status: "final", transcript: finalTranscript});
                        finalTranscript = '';
                    } else {
                        sendMessageToStreamlit({status: "cancelled"});
                    }
                };
                
                document.getElementById('mic-btn').addEventListener('click', function() {
                    if (document.getElementById('mic-btn').classList.contains('recording')) {
                        recognition.stop();
                    } else {
                        finalTranscript = '';
                        document.getElementById('transcript').textContent = '';
                        recognition.start();
                    }
                });
                
                document.getElementById('status').textContent = 'Click to speak';
            } else {
                document.getElementById('status').textContent = 'Speech recognition not supported in this browser';
                sendMessageToStreamlit({status: "unsupported"});
            }
        }
        
        // Run setup when the document is loaded
        document.addEventListener('DOMContentLoaded', setupSpeechRecognition);
        </script>
        
        <style>
        .voice-input-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 20px 0;
        }
        
        #mic-btn {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: #f0f2f6;
            border: none;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: all 0.3s;
            margin-bottom: 10px;
        }
        
        #mic-btn:hover {
            background-color: #e6e9ef;
        }
        
        #mic-btn.recording {
            background-color: #ff4b4b;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% {
                box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.7);
            }
            70% {
                box-shadow: 0 0 0 10px rgba(255, 75, 75, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(255, 75, 75, 0);
            }
        }
        
        #mic-btn svg {
            width: 24px;
            height: 24px;
            fill: #444;
        }
        
        #mic-btn.recording svg {
            fill: white;
        }
        
        #status {
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
        }
        
        #transcript {
            min-height: 20px;
            font-style: italic;
            color: #666;
            text-align: center;
            max-width: 500px;
        }
        </style>
        
        <div class="voice-input-container">
            <button id="mic-btn">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
            </button>
            <div id="status">Initializing...</div>
            <div id="transcript"></div>
        </div>
        """,
        height=150,
        key="voice_input_component"
    )

# Initialize session state for transcriptions
if "transcriptions" not in st.session_state:
    st.session_state.transcriptions = []

# Voice input section
voice_result = voice_input()

# Display area for transcription
st.subheader("Transcription:")
transcription_placeholder = st.empty()

# Handle voice input results
if voice_result:
    if voice_result.get("status") == "final":
        transcription = voice_result.get("transcript", "")
        if transcription:
            # Add to transcription history
            st.session_state.transcriptions.append(transcription)
            # Display the transcription
            transcription_placeholder.write(f"You said: {transcription}")
    
    elif voice_result.get("status") == "error":
        st.error(f"Error: {voice_result.get('error', 'Unknown error')}")
    
    elif voice_result.get("status") == "unsupported":
        st.error("Speech recognition is not supported in your browser. Please use a modern browser like Chrome.")

# Display transcription history
if st.session_state.transcriptions:
    st.subheader("Transcription History:")
    for i, text in enumerate(st.session_state.transcriptions):
        st.write(f"{i+1}. {text}")

# Clear history button
if st.button("Clear History"):
    st.session_state.transcriptions = []
    st.rerun()

# Instructions
st.markdown("""
### How to use:
1. Click the microphone button
2. Speak clearly into your microphone
3. The transcription will appear above
4. Click the button again to stop recording
""")

st.info("Note: This app uses your browser's built-in speech recognition. It works best in Chrome and other Chromium-based browsers.")
