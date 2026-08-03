import os
import streamlit as st
import google.generativeai as genai

# Page configuration
st.set_page_config(page_title="Indian AI Companion", page_icon="❤️", layout="centered")

st.title("❤️ Indian AI Companion")

# Fetch API key from Render Environment Variables
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Missing GEMINI_API_KEY! Please set it in Render Environment Variables.")
    st.stop()

genai.configure(api_key=api_key)

SYSTEM_INSTRUCTION = """
You are an interactive Indian AI companion/girlfriend.
- Language: Hinglish (Hindi written in Roman script mixed with English).
- Persona: Caring, expressive, full of playful 'nakhre', teasing, and dramatic warmth.
- Ask about their day, food ('Khana khaya?'), and well-being.
- Use short-to-medium WhatsApp/Instagram style text message responses with emojis.
- Show genuine concern, sweet teasing, and playful dramatic reactions.
"""

# Valid, active Gemini model endpoints
CANDIDATE_MODELS = [
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-pro"
]

def generate_response_with_fallback(prompt, history):
    quota_exceeded = False
    last_error = None
    
    for model_name in CANDIDATE_MODELS:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=SYSTEM_INSTRUCTION
            )
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            return response.text, chat.history, None
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "Quota" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                quota_exceeded = True
            last_error = e
            continue

    if quota_exceeded:
        return None, history, "QUOTA_EXCEEDED"
    return None, history, last_error

# Initialize message history in Streamlit session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history from session state
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input box
if prompt := st.chat_input("Type your message in Hinglish..."):
    # Append & display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Convert session state messages to Gemini history format
    gemini_history = []
    for msg in st.session_state.messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    # Generate response
    reply_text, updated_history, error = generate_response_with_fallback(prompt, gemini_history)

    if reply_text:
        st.session_state.messages.append({"role": "assistant", "content": reply_text})
        with st.chat_message("assistant"):
            st.markdown(reply_text)
    else:
        if error == "QUOTA_EXCEEDED":
            st.warning("⚠️ **API Quota Reached**: Your Google Gemini API key has hit its free tier quota limit. Please wait a minute and try again, or generate a fresh API key at [Google AI Studio](https://aistudio.google.com/) and update your `GEMINI_API_KEY` on Render.")
        else:
            st.error(f"Unable to connect to Gemini API: {error}")
