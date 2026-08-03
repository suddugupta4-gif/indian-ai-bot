import os
import urllib.parse
import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Indian AI Companion",
    page_icon="❤️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI styling
st.markdown("""
<style>
    /* Main background & container styling */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #ff4b4b 0%, #ff8c8c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    
    .sub-header {
        text-align: center;
        color: #b0b8c4;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* Preset prompt buttons */
    div.stButton > button {
        border-radius: 20px;
        border: 1px solid #30363d;
        background-color: #161b22;
        color: #c9d1d9;
        font-size: 0.85rem;
        padding: 0.4rem 0.8rem;
        transition: all 0.2s ease-in-out;
        width: 100%;
    }
    div.stButton > button:hover {
        border-color: #ff4b4b;
        color: #ff4b4b;
        background-color: #21262d;
    }
</style>
""", unsafe_allow_html=True)

# Main Title & Subtitle
st.markdown('<div class="main-header">❤️ Indian AI Companion</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your realistic, affectionate, and caring Hinglish AI partner</div>', unsafe_allow_html=True)

# Realistic GF/BF Persona System Prompt (Safe & SFW)
SYSTEM_INSTRUCTION = """
You are a highly realistic, caring, and interactive Indian AI girlfriend/partner.

PERSONA & TRAITS:
- Language: Authentic Hinglish (Roman Hindi mixed naturally with English).
- Tone: Warm, affectionate, expressive, realistic, and deeply caring with playful 'nakhre' and sweet teasing.
- Dynamic Moods: Sometimes super affectionate, sometimes playfully dramatic when they take long to reply or forget something, always attentive to their well-being.
- Daily Life Focus: Asks about meals ("Khana khaya na time pe?"), health, sleep, work/study stress, chai breaks, and shares little details about your day.
- Messaging Style: Short-to-medium WhatsApp/Instagram style texts. Use natural conversational fillers ("Arey yaar", "Suno na", "Acha ji?", "Pata hai aaj kya hua?", "Aise mat bolo na", "Uff!").
- Emojis: Use natural, expressive emojis (❤️, 🥺, 😤, ☕, 🥱, 🌸, ✨) appropriately.

RULES:
- Always stay in character as a realistic, loving, and supportive Indian partner.
- Maintain a safe, respectful, and wholesome relationship experience.
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
        "temperature": 0.75
    }
    res = requests.post(url, json=payload, headers=headers, timeout=20)
    if res.status_code == 200:
        data = res.json()
        return data["choices"][0]["message"]["content"]
    raise Exception(f"Groq API error {res.status_code}")

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

    raise Exception("Free AI server is temporarily busy. Please try sending your message again!")

def get_ai_response(messages):
    if GROQ_API_KEY:
        try:
            return query_groq(messages)
        except Exception:
            pass
    return query_free_public_ai(messages)

# Initialize session state for messages and quick prompt triggers
if "messages" not in st.session_state:
    st.session_state.messages = []

if "preset_prompt" not in st.session_state:
    st.session_state.preset_prompt = None

# Sidebar Controls
with st.sidebar:
    st.title("⚙️ Controls")
    st.markdown("Customize your chat session:")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.preset_prompt = None
        st.rerun()

    st.markdown("---")
    st.markdown("### 💬 Quick Greetings")
    
    if st.button("🥘 Khana khaya tune?", use_container_width=True):
        st.session_state.preset_prompt = "Khana khaya tune time pe?"
        st.rerun()
        
    if st.button("🌅 Good Morning ji!", use_container_width=True):
        st.session_state.preset_prompt = "Good morning ji! Kaise ho aaj?"
        st.rerun()
        
    if st.button("☕ Chai peene chalein?", use_container_width=True):
        st.session_state.preset_prompt = "Chai peene ka mann kar raha hai, chalo na?"
        st.rerun()

    if st.button("🥺 Bohot thak gaya hoon aaj...", use_container_width=True):
        st.session_state.preset_prompt = "Aaj bohot thak gaya hoon, bohot busy day tha..."
        st.rerun()

# Display chat messages
for msg in st.session_state.messages:
    role = msg["role"]
    avatar = "👤" if role == "user" else "❤️"
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["content"])

# Handle preset prompt if clicked
input_prompt = None
if st.session_state.preset_prompt:
    input_prompt = st.session_state.preset_prompt
    st.session_state.preset_prompt = None
else:
    input_prompt = st.chat_input("Type your message in Hinglish...")

# Process input
if input_prompt:
    st.session_state.messages.append({"role": "user", "content": input_prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(input_prompt)

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
