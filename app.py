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

# Candidate models to try in order
CANDIDATE_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro"
]

def get_working_model_name():
    try:
        supported = [
            m.name.replace("models/", "") 
            for m in genai.list_models() 
            if "generateContent" in m.supported_generation_methods
        ]
        for candidate in CANDIDATE_MODELS:
            if candidate in supported:
                return candidate
        if supported:
            return supported[0]
    except Exception:
        pass
    return "gemini-2.0-flash"

if "selected_model" not in st.session_state:
    st.session_state.selected_model = get_working_model_name()

model = genai.GenerativeModel(
    model_name=st.session_state.selected_model,
    system_instruction=SYSTEM_INSTRUCTION
)

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

    # Get response from Gemini with fallback
    try:
        response = st.session_state.chat.send_message(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)
    except Exception as e:
        # Fallback to another model if current fails
        fallback_success = False
        for fallback_name in CANDIDATE_MODELS:
            if fallback_name != st.session_state.selected_model:
                try:
                    fallback_model = genai.GenerativeModel(
                        model_name=fallback_name,
                        system_instruction=SYSTEM_INSTRUCTION
                    )
                    st.session_state.chat = fallback_model.start_chat(history=st.session_state.chat.history)
                    st.session_state.selected_model = fallback_name
                    response = st.session_state.chat.send_message(prompt)
                    with st.chat_message("assistant"):
                        st.markdown(response.text)
                    fallback_success = True
                    break
                except Exception:
                    continue
        if not fallback_success:
            st.error(f"Error generating response: {e}")
