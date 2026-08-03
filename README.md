# Indian AI Companion Chatbot ❤️

An interactive Indian AI Companion chatbot application built with Streamlit and Google Gemini API, ready to deploy on Render.com.

## Features
- **Authentic Hinglish & English Persona**: Converses naturally in Roman Hindi / Hinglish and English.
- **Realistic Emotions**: Expresses care, playful "nakhre", teasing, and daily check-ins.
- **Streamlit Chat UI**: Clean, responsive messaging interface.

## Deployment on Render.com

1. Sign in to [Render.com](https://render.com/).
2. Click **New +** > **Web Service**.
3. Connect your GitHub repository `indian-ai-bot`.
4. Configure settings:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - **Instance Type:** Free
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY`: *(Your Google Gemini API Key)*
6. Click **Create Web Service**.
