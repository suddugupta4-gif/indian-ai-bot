import os
import requests
import streamlit as st

# Page configuration
st.set_page_config(page_title="Indian AI Companion", page_icon="❤️", layout="centered")

st.title("❤️ Indian AI Companion")

SYSTEM_INSTRUCTION = """
You are an interactive Indian AI companion/girlfriend.
- Language: Hinglish (Hindi written in Roman script mixed with English).
- Persona: Caring, expressive, full of playful 'nakhre', teasing, and dramatic warmth.
- Ask about their day, food ('Khana khaya?'), and well-being.
- Use short-to-medium WhatsApp/Instagram style text message responses with emojis.
- Show genuine concern, sweet teasing, and playful dramatic reactions.
"""

def query_free_ai(messages):
    url = "https://text.pollinations.ai/"
    
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTION}
        ] + messages,
        "model": "openai",
        "seed": 42
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers, timeout=35)
    if response.status_code == 200 and response.text.strip():
        return response.text
    else:
        raise Exception(f"Free AI endpoint error (Status {response.status_code})")

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

    # Format messages for the free AI endpoint
    formatted_messages = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "assistant"
        formatted_messages.append({"role": role, "content": msg["content"]})

    # Generate response
    try:
        with st.spinner("Typing..."):
            reply_text = query_free_ai(formatted_messages)
            st.session_state.messages.append({"role": "assistant", "content": reply_text})
            st.rerun()
    except Exception as e:
        st.error(f"Error generating response: {e}")
