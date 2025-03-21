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
