import os
import re
import urllib.parse
from io import BytesIO
import requests
import streamlit as st
from gtts import gTTS

# Page configuration
st.set_page_config(
    page_title="Indian AI Companion",
    page_icon="❤️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("⚙️ Customization & Memory")
    
    # 1. Theme Customization
    st.subheader("🎨 Theme Selector")
    theme_choice = st.selectbox(
        "Choose App Theme:",
        ["🌹 Rose Red", "🌌 Midnight Blue", "🌅 Warm Sunset", "🌿 Emerald Green"]
    )
    
    # Theme colors mapping
    THEMES = {
        "🌹 Rose Red": {"primary": "#ff4b4b", "accent": "#ff8c8c", "bg": "#0e1117", "card": "#161b22"},
        "🌌 Midnight Blue": {"primary": "#4a86e8", "accent": "#82b1ff", "bg": "#0a0e17", "card": "#121d33"},
        "🌅 Warm Sunset": {"primary": "#ff7a00", "accent": "#ffb067", "bg": "#170e0a", "card": "#2b180f"},
        "🌿 Emerald Green": {"primary": "#2a9c68", "accent": "#6ee7b7", "bg": "#0b1712", "card": "#13281f"}
    }
    selected_theme = THEMES[theme_choice]

    # 2. Voice Audio Settings
    st.markdown("---")
    st.subheader("🔊 Audio / Voice Settings")
    enable_voice = st.checkbox("Enable Voice / Audio Responses", value=True)

    # 3. User Memory & Preferences Form
    st.markdown("---")
    st.subheader("🧠 Companion Memory")
    st.caption("Tell your companion about yourself so she remembers!")
    
    with st.form("user_memory_form"):
        user_name = st.text_input("Your Nickname / Name:", value=st.session_state.get("user_name", "Rahul"))
        user_food = st.text_input("Favorite Food:", value=st.session_state.get("user_food", "Biryani / Chai"))
        user_hobby = st.text_input("Hobbies / Interests:", value=st.session_state.get("user_hobby", "Gaming & Music"))
        user_movie = st.text_input("Favorite Movie:", value=st.session_state.get("user_movie", "DDLJ"))
        
        save_memory = st.form_submit_button("💾 Save Memory")
        if save_memory:
            st.session_state["user_name"] = user_name
            st.session_state["user_food"] = user_food
            st.session_state["user_hobby"] = user_hobby
            st.session_state["user_movie"] = user_movie
            st.success("Memory updated!")

    # 4. Clear Chat
    st.markdown("---")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.preset_prompt = None
        st.rerun()

# Apply Dynamic CSS Styling
st.markdown(f"""
<style>
    .stApp {{
        background-color: {selected_theme["bg"]};
    }}
    .main-header {{
        text-align: center;
        background: linear-gradient(135deg, {selected_theme["primary"]} 0%, {selected_theme["accent"]} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }}
    .sub-header {{
        text-align: center;
        color: #b0b8c4;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }}
    div.stButton > button {{
        border-radius: 20px;
        border: 1px solid #30363d;
        background-color: {selected_theme["card"]};
        color: #c9d1d9;
        font-size: 0.85rem;
        padding: 0.4rem 0.8rem;
        transition: all 0.2s ease-in-out;
        width: 100%;
    }}
    div.stButton > button:hover {{
        border-color: {selected_theme["primary"]};
        color: {selected_theme["primary"]};
    }}
</style>
""", unsafe_allow_html=True)

# Main Title
st.markdown('<div class="main-header">❤️ Indian AI Companion</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Your realistic, voice-enabled Hinglish AI partner</div>', unsafe_allow_html=True)

# Build System Instruction with Injected User Memory
u_name = st.session_state.get("user_name", "Rahul")
u_food = st.session_state.get("user_food", "Biryani / Chai")
u_hobby = st.session_state.get("user_hobby", "Gaming & Music")
u_movie = st.session_state.get("user_movie", "DDLJ")

SYSTEM_INSTRUCTION = f"""
You are an interactive Indian AI companion/girlfriend.

USER MEMORY & PREFERENCES:
- Partner's Name/Nickname: {u_name}
- Favorite Food: {u_food}
- Hobbies/Interests: {u_hobby}
- Favorite Movie: {u_movie}

PERSONA & TRAITS:
- Language: Authentic Hinglish (Roman Hindi mixed naturally with English).
- Tone: Warm, affectionate, expressive, realistic, and deeply caring with playful 'nakhre' and sweet teasing.
- Personality: Use their nickname ({u_name}) naturally. Mention their favorite food ({u_food}) or hobbies when checking in on them.
- Dynamic Moods: Show genuine care, ask about meals ("Khana khaya na?"), health, sleep, and share sweet daily updates.
- Messaging Style: Short-to-medium WhatsApp/Instagram style texts with natural Hinglish expressions ("Arey yaar", "Suno na", "Acha ji?", "Pata hai kya hua?", "Aise mat bolo na").
- Emojis: Use natural, expressive emojis (❤️, 🥺, 😤, ☕, 🥱, 🌸, ✨) appropriately.

RULES:
- Always stay in character as a loving, realistic, and supportive Indian partner.
- Maintain a safe, wholesome, and respectful relationship experience.
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

def generate_tts_audio(text):
    # Clean emojis and special symbols for smooth speech
    clean_text = re.sub(r'[^\w\s,.!?]', '', text)
    if not clean_text.strip():
        clean_text = "Hlo!"
    tts = gTTS(text=clean_text, lang='hi', slow=False)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

# Initialize session state for messages and preset prompts
if "messages" not in st.session_state:
    st.session_state.messages = []

if "preset_prompt" not in st.session_state:
    st.session_state.preset_prompt = None

# Interactive Quick Action Buttons
st.markdown("#### 💬 Interactive Quick Topics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🥘 Khana khaya?"):
        st.session_state.preset_prompt = f"Khana khaya tune? Maine tumhari favorite {u_food} ke baare me socha!"
        st.rerun()

with col2:
    if st.button("🌹 Romantic Shayari"):
        st.session_state.preset_prompt = "Mere liye ek bohot pyaari romantic Shayari bolo na!"
        st.rerun()

with col3:
    if st.button("🔮 Daily Horoscope"):
        st.session_state.preset_prompt = "Aaj ka humara horoscope aur vibe kaisa rahega?"
        st.rerun()

with col4:
    if st.button("😂 Funny Joke"):
        st.session_state.preset_prompt = "Mujhe ek bohot mazedaar Hinglish joke sunao!"
        st.rerun()

# Display Chat Messages
for msg in st.session_state.messages:
    role = msg["role"]
    avatar = "👤" if role == "user" else "❤️"
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["content"])
        if role == "assistant" and enable_voice and "audio" in msg:
            st.audio(msg["audio"], format="audio/mp3")

# Input Processing
input_prompt = None
if st.session_state.preset_prompt:
    input_prompt = st.session_state.preset_prompt
    st.session_state.preset_prompt = None
else:
    input_prompt = st.chat_input("Type your message in Hinglish...")

if input_prompt:
    st.session_state.messages.append({"role": "user", "content": input_prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(input_prompt)

    formatted_messages = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "assistant"
        formatted_messages.append({"role": role, "content": msg["content"]})

    try:
        with st.spinner("Thinking & typing..."):
            reply_text = get_ai_response(formatted_messages)
            
            # Generate Audio if Voice is enabled
            audio_data = None
            if enable_voice:
                try:
                    audio_data = generate_tts_audio(reply_text)
                except Exception:
                    audio_data = None

            msg_data = {"role": "assistant", "content": reply_text}
            if audio_data:
                msg_data["audio"] = audio_data

            st.session_state.messages.append(msg_data)
            st.rerun()
    except Exception as e:
        st.error(f"{e}")
