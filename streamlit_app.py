import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
import streamlit.components.v1 as components

# Load environment variables from .env file (if it exists)
load_dotenv()

st.set_page_config(
    page_title="Voice Chat with Mistral", 
    page_icon="🎙️",
    layout="wide"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "recording" not in st.session_state:
    st.session_state.recording = False
if "transcription" not in st.session_state:
    st.session_state.transcription = ""

st.title("Voice Chat with Mistral AI")
st.write("Have a conversation with Mistral using your voice!")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # API key input
    api_key = st.text_input(
        "Enter your Mistral API key",
        value=os.getenv("MISTRAL_API_KEY", ""),
        type="password"
    )
    
    # Model selection
    model = st.selectbox(
        "Select Mistral model",
        [
            "mistral-tiny",
            "mistral-small",
            "mistral-medium",
            "mistral-large-latest"
        ],
        index=0
    )
    
    # Save API key option
    if st.button("Save API Key"):
        if not api_key:
            st.error("Please enter an API key to save.")
        else:
            try:
                with open(".env", "w") as f:
                    f.write(f"MISTRAL_API_KEY={api_key}")
                st.success("API key saved to .env file!")
            except Exception as e:
                st.error(f"Failed to save API key: {str(e)}")
    
    st.divider()
    
    # Clear conversation button
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Main chat area
chat_container = st.container()

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

# Display chat messages
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Function to call Mistral API
def call_mistral_api(messages, api_key, model):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    response = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload)
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"API Error: {response.status_code}")
        st.code(response.text)
        return None

# Text input for typing
text_input = st.text_input("Type your message:", key="text_input")
if text_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": text_input})
    
    # Display user message
    with chat_container:
        with st.chat_message("user"):
            st.write(text_input)
    
    # Get AI response if API key is provided
    if api_key:
        with st.spinner("Mistral is thinking..."):
            # Format messages for API
            api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            
            # Call API
            result = call_mistral_api(api_messages, api_key, model)
            
            if result:
                ai_response = result["choices"][0]["message"]["content"]
                
                # Add AI response to chat
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                
                # Display AI response
                with chat_container:
                    with st.chat_message("assistant"):
                        st.write(ai_response)
    else:
        st.warning("Please enter your Mistral API key in the sidebar.")
    
    # Rerun to update UI and clear input
    st.rerun()

# Voice input section
st.subheader("Or speak your message:")
voice_result = voice_input()

# Handle voice input results
if voice_result:
    if voice_result.get("status") == "final":
        transcription = voice_result.get("transcript", "")
        if transcription:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": transcription})
            
            # Get AI response if API key is provided
            if api_key:
                with st.spinner("Mistral is thinking..."):
                    # Format messages for API
                    api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    
                    # Call API
                    result = call_mistral_api(api_messages, api_key, model)
                    
                    if result:
                        ai_response = result["choices"][0]["message"]["content"]
                        
                        # Add AI response to chat
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
            # Rerun to update UI
            st.rerun()
    
    elif voice_result.get("status") == "unsupported":
        st.error("Speech recognition is not supported in your browser. Please use a modern browser like Chrome.")

# Instructions at the bottom
with st.expander("How to use this app"):
    st.markdown("""
    1. Enter your Mistral API key in the sidebar
    2. Choose a Mistral model
    3. Start a conversation by:
       - Typing in the text box, or
       - Clicking the microphone button and speaking
    4. View the conversation history above
    5. Clear the conversation using the button in the sidebar
    """)
