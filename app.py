import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import base64
import numpy as np

from streamlit_mic_recorder import speech_to_text
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage

# --- Load environment variables ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)
tavily_search = TavilySearch(api_key=TAVILY_API_KEY, max_results=3)

# --- UI CSS ---
st.markdown("""
    <style>
        body, .stApp {background: #f9fafb !important; font-family: 'Montserrat', 'Segoe UI', sans-serif;}
        .ai-logo {display: flex; justify-content: center; align-items: center; margin-top: 2rem; margin-bottom: 0.5rem;}
        .ai-title {text-align: center; font-size: 2.5rem; font-weight: 700; color: #222; margin-bottom: 0.3rem; letter-spacing: -1px;}
        .ai-subtitle {text-align: center; color: #4caf50; font-size: 1.1rem; margin-bottom: 2.5rem;}
        .ai-intro {text-align: center; font-size: 1rem; color: #555; margin-bottom: 2rem; max-width: 700px; margin-left: auto; margin-right: auto;}
        .searchbar-container {display: flex; flex-direction: column; align-items: center; margin-bottom: 2rem;}
        .searchbar-main {display: flex; align-items: center; background: #fff; border-radius: 2rem; border: 2px solid #e0e0e0; box-shadow: 0 2px 12px #a5d6a733; padding: 0.2rem 1.4rem 0.2rem 1.4rem; width: 100%; max-width: 600px;}
        .searchbar-main input[type="text"] {flex: 1; border: none; background: transparent; font-size: 1.25rem; color: #222; padding: 18px 10px 18px 0; outline: none;}
        .searchbar-main input[type="text"]::placeholder {color: #bdbdbd; font-size: 1.15rem;}
        .searchbar-main .file-upload-label {margin-left: 0.5rem; cursor: pointer; font-size: 1.7rem; color: #4caf50; transition: color 0.2s;}
        .searchbar-main .file-upload-label:hover {color: #388e3c;}
        .searchbar-main .submit-btn {background: #4caf50; border: none; border-radius: 50%; width: 2.6rem; height: 2.6rem; margin-left: 0.5rem; color: #fff; font-size: 1.3rem; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: background 0.2s;}
        .searchbar-main .submit-btn:hover {background: #388e3c;}
        .chat-avatar {width: 38px; height: 38px; border-radius: 50%; background: #fff; border: 2px solid #4caf50; display: inline-block; margin-right: 0.7rem; vertical-align: middle;}
        .chat-bubble {display: flex; align-items: flex-start; margin-bottom: 1.1rem;}
        .chat-bubble.bot {flex-direction: row;}
        .chat-bubble.user {flex-direction: row-reverse;}
        .bubble-content {background: #f9fbe7; border-radius: 18px; padding: 16px 20px; box-shadow: 0 2px 8px #a5d6a733; color: #2e7d32; font-size: 1.07rem; max-width: 65vw; min-width: 120px;}
        .bubble-content.user {background: #c8e6c9; color: #1b5e20;}
    </style>
""", unsafe_allow_html=True)

# --- Logo ---
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

# --- Title and subtitle ---
st.markdown('<div class="ai-title">Terrคi: The Futuristic AI Farming Guide</div>', unsafe_allow_html=True)
st.markdown('<div class="ai-subtitle">Empowering Indian farmers with AI, real-time insights, and smart agriculture innovations</div>', unsafe_allow_html=True)

# --- Introduction prompt from your previous code ---
st.markdown(
    """
    <div class="ai-intro">
    🤖 I am Terrคi, developed by Prudhvi, an engineer passionate about Indian agriculture.  
    My mission is to empower Indian farmers with practical, region-specific guidance for every stage of cultivation,  
    combining AI with real-time knowledge and innovation.
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Session state for chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_user_message" not in st.session_state:
    st.session_state.pending_user_message = None

# --- Voice input (browser-based) ---
voice_text = speech_to_text(language='en', use_container_width=True, just_once=True, key='voice_input')
if voice_text:
    st.session_state.pending_user_message = {"query": voice_text, "image_bytes": None, "image_filename": None}

# --- Chat history display ---
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f"""
            <div class="chat-bubble user">
                <div class="chat-avatar"><img src="https://img.icons8.com/ios-filled/50/388e3c/user-male-circle.png" width="38" style="border-radius:50%;" /></div>
                <div class="bubble-content user">{message['content']}</div>
            </div>
            """, unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="chat-bubble bot">
                <div class="chat-avatar">{ai_logo_svg}</div>
                <div class="bubble-content">{message['content']}</div>
            </div>
            """, unsafe_allow_html=True
        )

# --- Search bar: text + paperclip + submit ---
with st.form("query_form", clear_on_submit=False):
    st.markdown('<div class="searchbar-container">', unsafe_allow_html=True)
    st.markdown('<div class="searchbar-main">', unsafe_allow_html=True)
    user_query = st.text_input(
        "", key="query", label_visibility="collapsed", placeholder="Type your question here..."
    )
    uploaded_file = st.file_uploader(
        "", type=["png", "jpg", "jpeg"], label_visibility="collapsed", accept_multiple_files=False, key="file"
    )
    st.markdown(
        '<label for="file-upload" class="file-upload-label" title="Attach image">📎</label>',
        unsafe_allow_html=True
    )
    submit = st.form_submit_button("➔", type="primary", use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- On submit: add pending user message to state ---
if submit:
    image_bytes = None
    image_filename = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        uploaded_file.seek(0)
        image_bytes = uploaded_file.read()
        image_filename = uploaded_file.name
    st.session_state.pending_user_message = {
        "query": user_query,
        "image_bytes": image_bytes,
        "image_filename": image_filename
    }

# --- Assistant response logic ---
def is_meta_query(q):
    meta_keywords = ["who are you", "created", "your name", "developer", "model", "prudhvi", "about you"]
    return any(kw in q.lower() for kw in meta_keywords)

def handle_meta_query():
    return (
        "👩‍🌾 I am Terrคi, developed by Prudhvi, an engineer passionate about Indian agriculture. "
        "My mission is to empower Indian farmers with practical, region-specific guidance for every stage of cultivation, "
        "combining AI with real-time knowledge and innovation."
    )

def get_rag_answer(question, image_bytes=None, image_filename=None):
    search_results = tavily_search.invoke({"query": question})
    image_base64 = base64.b64encode(image_bytes).decode("utf-8") if image_bytes else None
    if image_bytes:
        image_instruction = (
            "The user has attached a photo. Carefully analyze it for plant health, disease, pest, soil, or fertilizer issues. "
            "If a plant, say if it looks healthy or unhealthy, and suggest best fertilizers and modern techniques to improve growth. "
            "If unhealthy, explain the problems you see and suggest specific treatments. "
            "If fertilizer, soil, or other, explain what it is, its uses, and best practices. "
            "If you cannot identify the image, say so politely and suggest how to get more help."
        )
    else:
        image_instruction = (
            "No image is attached. Only answer based on the user's question and the search results."
        )
    system_prompt = (
        "You are Terrคi, a friendly and expert agricultural advisor for Indian farmers. "
        "You are given a farmer's question and a set of search results from trusted Indian sources.\n\n"
        f"{image_instruction}\n"
        "Your answer must follow this structure:\n"
        "1. **Image/Voice Analysis:** (if provided) What is in the image or query and your assessment.\n"
        "2. **Summary:** A direct, friendly answer to the farmer's question.\n"
        "3. **Step-by-step Solution:** Detailed, region-specific, actionable advice for the farmer.\n"
        "4. **Confidence Level:** High/Medium/Low, based on search result quality and input clarity.\n"
        "5. **Suggested Next Steps:** If the answer is incomplete, suggest where to get more info (e.g., local agri office, helpline, etc.).\n\n"
        f"Here are the search results:\n{search_results}\n\n"
        f"Farmer's Question:\n{question}\n\n"
        "Do NOT mention specific sources or web links in your answer. Use simple, respectful, and clear language."
    )
    messages = [SystemMessage(content=system_prompt)]
    if image_base64:
        messages.append(HumanMessage(
            content="Attached is a photo uploaded by the farmer (base64-encoded). Please analyze it as per the instructions.",
            additional_kwargs={"image_base64": image_base64, "filename": image_filename}
        ))
    else:
        messages.append(HumanMessage(content=question))
    response = llm.invoke(messages)
    answer = response.content.strip()
    return answer

def get_self_qa(question):
    prompt = (
        "Given this farmer's question, generate 2-3 related follow-up questions a farmer might ask. "
        "For each, give a detailed, region-specific answer. "
        "If possible, include local crop varieties, climate, and sustainable practices. "
        "Format:\nQ1: ...\nA1: ...\nQ2: ...\nA2: ...\n"
        f"Farmer's question: {question}"
    )
    messages = [
        SystemMessage(content="You are a helpful Indian farming assistant."),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages)
    return response.content.strip()

# --- Process pending user message and generate assistant reply ---
if st.session_state.pending_user_message:
    pending = st.session_state.pending_user_message
    q = pending["query"]
    image_bytes = pending["image_bytes"]
    image_filename = pending["image_filename"]

    # Show user message in chat
    st.session_state.messages.append({"role": "user", "content": q})

    # Generate assistant response
    if is_meta_query(q):
        response = handle_meta_query()
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        with st.spinner("Thinking..."):
            rag_answer = get_rag_answer(q, image_bytes=image_bytes, image_filename=image_filename)
            self_qa = get_self_qa(q)
            full_answer = rag_answer + "<br><hr><b>Other questions you may have:</b><br>" + self_qa
            st.session_state.messages.append({"role": "assistant", "content": full_answer})
    st.session_state.pending_user_message = None
    st.experimental_rerun()

# --- Footer ---
st.markdown(
    "<div style='text-align:center; color:#888888; margin-top:3rem; font-size:0.9rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi • May 2025"
    "</div>",
    unsafe_allow_html=True
)
