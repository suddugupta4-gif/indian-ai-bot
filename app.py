import os
import streamlit as st
import google.generativeai as genai

# Page configuration
st.set_page_config(page_title="Indian AI Companion", page_icon="❤️", layout="centered")

st.title("❤️ Indian AI Companion")

# Fetch API key from Render Environment Variables
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Missing GEMINI_API_KEY! Please add it in Render Environment Variables.")
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

@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )

model = get_model()

# Initialize chat session
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# Display chat history
for message in st.session_state.chat.history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# User input box
if prompt := st.chat_input("Type your message in Hinglish..."):
    # Display user input
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from Gemini
    response = st.session_state.chat.send_message(prompt)

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response.text)
