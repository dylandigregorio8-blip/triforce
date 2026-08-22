import streamlit as st
import time
import base64
import json
import os
from dotenv import load_dotenv

# Try importing the regex detector from your folder
try:
    from regex_detector import regex_detector
except ImportError:
    # Fallback function if regex_detector.py isn't found yet
    def regex_detector(text):
        return []

# --- Load environment variables ---
load_dotenv()

# 1. Set page configuration (MUST be the first Streamlit command)
st.set_page_config(page_title="AI Chatbot", page_icon="🤖")

# Function to get base64 encoded image to embed in CSS
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

# --- INJECT CUSTOM CSS FOR FIXED BACKGROUND ---
img_path = "pic.jpg" # Make sure this matches your image name!
try:
    img_base64 = get_base64_image(img_path)

    custom_css = f"""
    <style>
    /* Target the main Streamlit app container */
    .stApp {{
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Semi-transparent white overlay to ensure all text is readable */
    .stApp > header {{
        background-color: transparent;
    }}
    
    .block-container {{
        background-color: rgba(255, 255, 255, 0.7);
        padding: 2rem;
        border-radius: 20px;
        margin-top: 20px;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
except FileNotFoundError:
    st.warning(f"Background image not found: {img_path}. Proceeding without background.")
# -----------------------------------------------

st.title("Swiss Data Airlock")

# 2. Initialize session state to store chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hallo. Ich bin cool"}
    ]

# 3. Display past messages on every app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- FILE EXPLORER BUTTON ---
with st.popover("📎 Attach File"):
    uploaded_file = st.file_uploader("Choose a file from your device")
    if uploaded_file is not None:
        st.success(f"Selected: {uploaded_file.name}")

# --- BACKEND FUNCTIONS (from main.py) ---
def local_ai(document: str):
    # Local AI extraction stub[cite: 6, 8]
    return ["Swisscom AG", "Dr. Ursula Meier", "Coop Supermarkt Bern"]

def replace(identifiers, document: str):
    # Replace items in document[cite: 6, 8]
    return document, []

# 4. React to user input
if prompt := st.chat_input("Type your message here..."):
    
    # Display user message and add to state
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 5. Generate and display assistant response using your backend pipeline
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # --- EXECUTE PROCESSING PIPELINE ---
        document = prompt
        regex_identifiers = regex_detector(document)
        ai_identifiers = local_ai(document)
        
        combined_identifiers = sorted(
            set(regex_identifiers + ai_identifiers), 
            key=len, 
            reverse=True
        )
        
        replacement_result, replacements_mapping = replace(combined_identifiers, document)
        full_response = replacement_result
        # -----------------------------------
        
        # Simulating a streaming response for the UI
        displayed_text = ""
        for chunk in full_response.split():
            displayed_text += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(displayed_text + "▌")
            
        message_placeholder.markdown(full_response)
    
    # Add assistant response to state
    st.session_state.messages.append({"role": "assistant", "content": full_response})