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

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def query_groq(messages):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": SYSTEM_INSTRUCTION}] + messages,
        "temperature": 0.7
    }
    res = requests.post(url, json=payload, headers=headers, timeout=20)
    if res.status_code == 200:
        data = res.json()
        return data["choices"][0]["message"]["content"]
    raise Exception(f"Groq API error {res.status_code}: {res.text}")

def query_free_public_ai(messages):
    FREE_MODELS = ["mistral", "llama", "qwen-coder", "deepseek"]
    url = "https://text.pollinations.ai/"
    
    for model_name in FREE_MODELS:
        payload = {
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION}
            ] + messages,
            "model": model_name,
            "seed": 42
        }
        try:
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
            if res.status_code == 200 and res.text.strip():
                return res.text
        except Exception:
            continue

    # Simple GET fallback
    try:
        last_msg = messages[-1]["content"] if messages else "Hello"
        prompt_text = f"System: {SYSTEM_INSTRUCTION}\nUser: {last_msg}\nAssistant:"
        encoded_prompt = urllib.parse.quote(prompt_text)
        res = requests.get(f"https://text.pollinations.ai/{encoded_prompt}?model=mistral", timeout=15)
        if res.status_code == 200 and res.text.strip():
            return res.text
    except Exception:
        pass

    raise Exception("Free AI server is temporarily busy. Please try again in a few seconds!")

def get_ai_response(messages):
    # Priority 1: Groq API (Super fast & 100% free 14,400 req/day)
    if GROQ_API_KEY:
        try:
            return query_groq(messages)
        except Exception:
            pass
            
    # Priority 2: Free Public Inference
    return query_free_public_ai(messages)

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

    # Format messages for AI API
    formatted_messages = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "assistant"
        formatted_messages.append({"role": role, "content": msg["content"]})

    # Generate response
    try:
        with st.spinner("Typing..."):
            reply_text = get_ai_response(formatted_messages)
            st.session_state.messages.append({"role": "assistant", "content": reply_text})
            st.rerun()
    except Exception as e:
        st.error(f"{e}")
