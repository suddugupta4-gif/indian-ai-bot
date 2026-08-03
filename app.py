import os
import urllib.parse
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
    
    # Free models that do not require payment (Status 402)
    FREE_MODELS = ["mistral", "llama", "qwen-coder", None]
    
    for model_name in FREE_MODELS:
        payload = {
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION}
            ] + messages,
            "seed": 42
        }
        if model_name:
            payload["model"] = model_name

        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=25)
            if response.status_code == 200 and response.text.strip():
                return response.text
        except Exception:
            continue

    # Fallback GET request if POST encounters issues
    try:
        last_msg = messages[-1]["content"] if messages else "Hello"
        prompt_text = f"System: {SYSTEM_INSTRUCTION}\nUser: {last_msg}\nAssistant:"
        encoded_prompt = urllib.parse.quote(prompt_text)
        res = requests.get(f"https://text.pollinations.ai/{encoded_prompt}?model=mistral", timeout=25)
        if res.status_code == 200 and res.text.strip():
            return res.text
    except Exception as e:
        raise e

    raise Exception("Free AI server is temporarily busy. Please try sending your message again!")

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

    # Format messages for free AI API
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
        st.error(f"{e}")
