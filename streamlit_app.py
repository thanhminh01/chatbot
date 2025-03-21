import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

st.set_page_config(page_title="Mistral API Tester", page_icon="🤖")

st.title("Mistral API Key Tester")
st.write("This app tests if your Mistral API key is working correctly.")

# API key input
api_key = st.text_input(
    "Enter your Mistral API key",
    value=os.getenv("MISTRAL_API_KEY", ""),
    type="password"
)

# Model selection
model = st.selectbox(
    "Select Mistral model to test",
    [
        "mistral-tiny",
        "mistral-small",
        "mistral-medium",
        "mistral-large-latest"
    ],
    index=0
)

# Test prompt
test_prompt = st.text_area(
    "Test prompt",
    value="Hello, can you tell me a short joke?",
    height=100
)

# Test button
if st.button("Test API Connection"):
    if not api_key:
        st.error("Please enter your Mistral API key.")
    else:
        with st.spinner("Testing API connection..."):
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": test_prompt}],
                    "temperature": 0.7,
                    "max_tokens": 200
                }
                
                response = requests.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers=headers,
                    data=json.dumps(payload)
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ API connection successful!")
                    
                    # Display response
                    st.subheader("API Response:")
                    response_content = result["choices"][0]["message"]["content"]
                    st.markdown(response_content)
                    
                    # Display raw JSON for debugging
                    with st.expander("View raw API response"):
                        st.json(result)
                else:
                    st.error(f"❌ API Error: {response.status_code}")
                    st.code(response.text)
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Save API key option
if st.checkbox("Save API key to .env file"):
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
st.markdown("### How to use this app")
st.markdown("""
1. Enter your Mistral API key in the field above
2. Select a model to test
3. Optionally modify the test prompt
4. Click "Test API Connection"
5. If successful, you'll see the model's response below
""")
