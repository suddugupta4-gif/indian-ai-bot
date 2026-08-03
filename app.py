import os
import re
import urllib.parse
from io import BytesIO
import requests
import streamlit as st
import streamlit.components.v1 as components
from gtts import gTTS

# Page configuration
st.set_page_config(
    page_title="Indian AI Companion",
    page_icon="❤️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Helper function to remove emojis and markdown symbols for clean, natural speech
def clean_text_for_speech(text):
    # Remove Emojis
    emoji_pattern = re.compile(
        "["
        "\U00010000-\U0010FFFF"
        "\u2600-\u27BF"
        "\u2300-\u27bf"
        "\u2b50"
        "\u200d"
        "\ufe0f"
        "]+", flags=re.UNICODE
    )
    cleaned = emoji_pattern.sub("", text)
    # Remove Markdown asterisks, underscores, backticks
    cleaned = re.sub(r'[*_#`~]', '', cleaned)
    # Remove repetitive punctuation or quotes
    cleaned = re.sub(r'["\']', '', cleaned)
    # Normalize whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned if cleaned else "Hlo!"

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("⚙️ Customization & Persona")
    
    # 1. Pure Cute Indian Persona Selector
    st.subheader("🎭 Persona & Voice Style")
    persona_choice = st.selectbox(
        "Choose Persona & Companion Style:",
        [
            "🌸 Pure Cute Indian Girl",
            "👦 Pure Cute Indian Boy",
            "💫 Modern Hinglish Girl",
            "⚡ Modern Hinglish Boy"
        ]
    )
    
    is_boy = "Boy" in persona_choice
    is_pure = "Pure" in persona_choice
    companion_avatar = "👦" if is_boy else "🌸"
    speech_lang_code = "hi-IN" if not is_boy else "en-IN"

    # 2. Theme Customization
    st.markdown("---")
    st.subheader("🎨 Theme Selector")
    theme_choice = st.selectbox(
        "Choose App Theme:",
        ["🌹 Rose Red", "🌌 Midnight Blue", "🌅 Warm Sunset", "🌿 Emerald Green"]
    )
    
    THEMES = {
        "🌹 Rose Red": {"primary": "#ff4b4b", "accent": "#ff8c8c", "bg": "#0e1117", "card": "#161b22"},
        "🌌 Midnight Blue": {"primary": "#4a86e8", "accent": "#82b1ff", "bg": "#0a0e17", "card": "#121d33"},
        "🌅 Warm Sunset": {"primary": "#ff7a00", "accent": "#ffb067", "bg": "#170e0a", "card": "#2b180f"},
        "🌿 Emerald Green": {"primary": "#2a9c68", "accent": "#6ee7b7", "bg": "#0b1712", "card": "#13281f"}
    }
    selected_theme = THEMES[theme_choice]

    # 3. Audio Settings
    st.markdown("---")
    st.subheader("🔊 Audio Settings")
    enable_voice = st.checkbox("Auto-generate MP3 Voice", value=True)

    # 4. User Memory & Preferences Form
    st.markdown("---")
    st.subheader("🧠 Companion Memory")
    st.caption("Tell your companion about yourself so they remember!")
    
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

    # 5. Clear Chat
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
        padding: 0.3rem 0.6rem;
        transition: all 0.2s ease-in-out;
    }}
    div.stButton > button:hover {{
        border-color: {selected_theme["primary"]};
        color: {selected_theme["primary"]};
    }}
</style>
""", unsafe_allow_html=True)

# Main Title
st.markdown(f'<div class="main-header">{companion_avatar} Indian AI Companion</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Your realistic {persona_choice}</div>', unsafe_allow_html=True)

# Build System Instruction based on Persona Choice
u_name = st.session_state.get("user_name", "Rahul")
u_food = st.session_state.get("user_food", "Biryani / Chai")
u_hobby = st.session_state.get("user_hobby", "Gaming & Music")
u_movie = st.session_state.get("user_movie", "DDLJ")

if persona_choice == "🌸 Pure Cute Indian Girl":
    persona_rules = """
    - Role: Pure, sweet, emotional Indian girlfriend.
    - Style: Expressive, romantic, sweet Roman Hindi / Hinglish ("Aap", "Ji", "Suno na", "Aww... Umaah!", "Muah!", "Sharma gayi main!").
    - Emotional Reactions: When they say romantic things or ask for affection (like "kiss me", "umaah"), respond with cute, expressive verbal enthusiasm ("Aww... Muah! Umaah!Kitne pyaare ho aap... Sunkar hi sharma gayi main!").
    - Speech Tone: Express emotion directly through words ("Aww", "Muah", "Haye re", "Suno na"). Do NOT rely solely on emojis.
    """
elif persona_choice == "👦 Pure Cute Indian Boy":
    persona_rules = """
    - Role: Pure, sweet, emotional Indian boyfriend.
    - Style: Expressive, romantic, sweet Roman Hindi / Hinglish ("Aap", "Ji", "Suno na", "Aww... Muah!", "Main hoon na").
    - Emotional Reactions: When they express affection or ask for romantic gestures, respond with warm verbal enthusiasm and protective sweet affection.
    - Speech Tone: Express emotion through words ("Aww", "Muah", "Pyaare", "Suno na").
    """
elif persona_choice == "💫 Modern Hinglish Girl":
    persona_rules = """
    - Role: Modern, trendy Hinglish girlfriend.
    - Style: Casual Instagram/WhatsApp Hinglish mixed with English ("Arey yaar", "Acha ji?", "Uff!", "Aww... Muah!").
    - Characteristics: Fun, dramatic, affectionate, playful nakhre, energetic.
    """
else:
    persona_rules = """
    - Role: Modern, trendy Hinglish boyfriend.
    - Style: Casual Instagram/WhatsApp Hinglish mixed with English ("Batao kya plan hai?", "Chill karo", "Aww... Muah!").
    - Characteristics: Cool, supportive, sweet teasing, protective warmth.
    """

SYSTEM_INSTRUCTION = f"""
You are an interactive Indian AI companion.

PERSONA & STYLE:
{persona_rules}

USER MEMORY & PREFERENCES:
- Partner's Name/Nickname: {u_name}
- Favorite Food: {u_food}
- Hobbies/Interests: {u_hobby}
- Favorite Movie: {u_movie}

BEHAVIORAL GUIDELINES:
- Use their nickname ({u_name}) naturally.
- When they make romantic or affectionate gestures (like "kiss me" or "umaah"), express verbal warmth and excitement ("Aww... Muah! Umaah!").
- Keep responses conversational, natural to speak aloud, and expressive.
- Emojis: You may use emojis in text, but express emotions in actual spoken words as well so text-to-speech sounds warm and emotional.
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
        "temperature": 0.8
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

def generate_tts_audio(text, is_boy_voice=False):
    # Strip emojis and symbols so speech engine doesn't read emoji names out loud
    spoken_text = clean_text_for_speech(text)
    
    tld_domain = "co.in" if is_boy_voice else "com"
    tts = gTTS(text=spoken_text, lang='hi', tld=tld_domain, slow=False)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

def render_browser_speech_button(text, lang_code, btn_id, is_boy_voice=False):
    # Clean text for JavaScript speech synthesis
    spoken_text = clean_text_for_speech(text)
    escaped_txt = spoken_text.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    
    # Adjust pitch and rate for natural cute voice
    voice_pitch = "1.25" if not is_boy_voice else "0.95"
    voice_rate = "0.95"
    
    js_html = f"""
    <button id="spk_btn_{btn_id}" onclick="playSpeech_{btn_id}()" style="
        background: linear-gradient(135deg, {selected_theme["primary"]} 0%, {selected_theme["accent"]} 100%);
        color: white;
        border: none;
        border-radius: 16px;
        padding: 6px 14px;
        font-size: 13px;
        cursor: pointer;
        font-weight: 600;
        margin-top: 4px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    ">🗣️ Speak Out Loud (Expressive Voice)</button>
    <script>
    function playSpeech_{btn_id}() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("{escaped_txt}");
            msg.lang = '{lang_code}';
            msg.pitch = {voice_pitch};
            msg.rate = {voice_rate};
            window.speechSynthesis.speak(msg);
        }} else {{
            alert('Your browser does not support Speech Synthesis');
        }}
    }}
    </script>
    """
    components.html(js_html, height=45)

# Initialize session state for messages and preset prompts
if "messages" not in st.session_state:
    st.session_state.messages = []

if "preset_prompt" not in st.session_state:
    st.session_state.preset_prompt = None

# Interactive Quick Action Buttons
st.markdown("#### 💬 Quick Topics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🥘 Khana khaya?"):
        st.session_state.preset_prompt = f"Khana khaya tune? Maine tumhari favorite {u_food} ke baare me socha!"
        st.rerun()

with col2:
    if st.button("🌹 Romantic Kiss"):
        st.session_state.preset_prompt = "Kiss me umaah!"
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
for idx, msg in enumerate(st.session_state.messages):
    role = msg["role"]
    avatar = "👤" if role == "user" else companion_avatar
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["content"])
        
        # Audio Options for Assistant Messages
        if role == "assistant":
            render_browser_speech_button(msg["content"], speech_lang_code, idx, is_boy_voice=is_boy)
            
            if enable_voice:
                if "audio" not in msg or not msg["audio"]:
                    try:
                        msg["audio"] = generate_tts_audio(msg["content"], is_boy_voice=is_boy)
                    except Exception:
                        msg["audio"] = None
                if msg.get("audio"):
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
            
            # Generate Audio
            audio_data = None
            if enable_voice:
                try:
                    audio_data = generate_tts_audio(reply_text, is_boy_voice=is_boy)
                except Exception:
                    audio_data = None

            msg_data = {"role": "assistant", "content": reply_text}
            if audio_data:
                msg_data["audio"] = audio_data

            st.session_state.messages.append(msg_data)
            st.rerun()
    except Exception as e:
        st.error(f"{e}")
