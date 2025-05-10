import streamlit as st
from PIL import Image
from streamlit_chat_widget import message, chat_input
from gtts import gTTS
import io

# Dummy AI function (replace with your RAG/LLM/image logic)
def get_ai_response(user_input, image=None):
    if image:
        return "I see you sent an image. (In production, image analysis would go here.)"
    if user_input:
        return f"Here’s my advice for your question: {user_input}"
    return "Please ask a question or upload an image."

def text_to_speech(text):
    tts = gTTS(text)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

# Branding and intro
st.markdown("""
    <style>
        .ai-logo {display: flex; justify-content: center; align-items: center; margin-top: 2rem; margin-bottom: 0.5rem;}
        .ai-title {text-align: center; font-size: 2.5rem; font-weight: 700; color: #222; margin-bottom: 0.3rem; letter-spacing: -1px;}
        .ai-subtitle {text-align: center; color: #4caf50; font-size: 1.1rem; margin-bottom: 2.5rem;}
        .ai-intro {text-align: center; font-size: 1rem; color: #555; margin-bottom: 2rem; max-width: 700px; margin-left: auto; margin-right: auto;}
    </style>
""", unsafe_allow_html=True)

ai_logo_svg = """
<div class="ai-logo">
<svg width="60" height="60" viewBox="0 0 72 72" fill="none">
  <defs>
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#4caf50" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="#81c784" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="stem" x1="36" y1="18" x2="36" y2="60" gradientUnits="userSpaceOnUse">
      <stop stop-color="#4caf50"/>
      <stop offset="1" stop-color="#388e3c"/>
    </linearGradient>
  </defs>
  <ellipse cx="36" cy="54" rx="22" ry="10" fill="url(#glow)"/>
  <path d="M36 54 Q46 34 62 22 Q46 28 36 54" fill="#aed581" opacity="0.92"/>
  <path d="M36 54 Q26 34 10 22 Q26 28 36 54" fill="#aed581" opacity="0.92"/>
  <rect x="34" y="18" width="4" height="36" rx="2" fill="url(#stem)"/>
  <ellipse cx="36" cy="18" rx="7" ry="9" fill="#aed581" stroke="#4caf50" stroke-width="1.5"/>
  <path d="M36 54 L36 68" stroke="#388e3c" stroke-width="2"/>
  <circle cx="36" cy="68" r="2.5" fill="#388e3c"/>
  <path d="M41 44 L53 51" stroke="#388e3c" stroke-width="2"/>
  <circle cx="53" cy="51" r="2.2" fill="#388e3c"/>
  <path d="M31 44 L19 51" stroke="#388e3c" stroke-width="2"/>
  <circle cx="19" cy="51" r="2.2" fill="#388e3c"/>
  <circle cx="36" cy="14" r="3" fill="#4caf50" stroke="#81c784" stroke-width="1"/>
  <text x="36" y="15.5" font-size="2.5" text-anchor="middle" fill="#1b5e20" font-family="Segoe UI">AI</text>
</svg>
</div>
"""
st.markdown(ai_logo_svg, unsafe_allow_html=True)

st.markdown('<div class="ai-title">Terrคi: The Futuristic AI Farming Guide</div>', unsafe_allow_html=True)
st.markdown('<div class="ai-subtitle">Empowering Indian farmers with AI, real-time insights, and smart agriculture innovations</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="ai-intro">
    🤖 I am Terrคi, developed by Prudhvi, an engineer passionate about Indian agriculture.<br>
    My mission is to empower Indian farmers with practical, region-specific guidance for every stage of cultivation, combining AI with real-time knowledge and innovation.
    </div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat history with images and audio
for msg in st.session_state.messages:
    if msg["role"] == "user":
        message(msg["content"], is_user=True, avatar_style="person")
        if msg.get("image"):
            st.image(msg["image"], caption="You sent this image", width=200)
    else:
        message(msg["content"], avatar_style="bottts")
        if msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")

# Input: text/voice (via chat_input), image (via uploader)
with st.container():
    user_input = chat_input("Type or record your question...")
    uploaded_image = st.file_uploader("Upload an image (optional)", type=["jpg", "jpeg", "png"], key="img")

    if user_input or uploaded_image:
        user_msg = {"role": "user", "content": user_input or "Image sent."}
        if uploaded_image:
            image_bytes = uploaded_image.read()
            user_msg["image"] = image_bytes
        st.session_state.messages.append(user_msg)

        # AI response
        ai_response = get_ai_response(user_input, image=uploaded_image)
        audio_bytes = text_to_speech(ai_response)
        st.session_state.messages.append({"role": "assistant", "content": ai_response, "audio": audio_bytes})

        st.experimental_rerun()

# Footer
st.markdown(
    "<div style='text-align:center; color:#888888; margin-top:3rem; font-size:0.9rem;'>"
    "Terrคi • Developed for Indian farmers • Powered by Prudhvi • May 2025"
    "</div>",
    unsafe_allow_html=True
)
