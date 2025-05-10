import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import base64

from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)
tavily_search = TavilySearch(api_key=TAVILY_API_KEY, max_results=3)

# --- Simple, clean theme ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap');
        .stApp {background-color: #ffffff; color: #333333; font-family: 'Montserrat', sans-serif;}
        .futuristic-logo {display: flex; justify-content: center; align-items: center; margin-bottom: -6px;}
        .main-title {text-align: center; color: #4caf50; font-size: 2.8rem; font-weight: 700; letter-spacing: 1.2px; margin-bottom: 0.3rem;}
        .subtitle {text-align: center; color: #666666; font-size: 1.25rem; margin-bottom: 2rem; font-weight: 500;}
        .stChatInput input {font-size: 1.1rem !important; background: #f1f8e9; border: 2px solid #81c784; border-radius: 12px; color: #2e7d32; padding-left: 14px; height: 40px;}
        .stChatInput input:focus {border-color: #4caf50 !important; outline: none; box-shadow: 0 0 8px #a5d6a7;}
        .stButton>button {background-color: #4caf50; color: #ffffff; font-weight: 700; border-radius: 12px; padding: 10px 24px; border: none;}
        .stButton>button:hover {background-color: #388e3c;}
        .stMarkdown {background-color: #f9fbe7; border-radius: 14px; padding: 22px; margin-bottom: 20px; color: #2e7d32 !important;}
        .stChatMessage > div {background-color: #e8f5e9 !important; border-radius: 14px !important; color: #1b5e20 !important; padding: 14px !important;}
        .stChatMessage.stChatMessage-user > div {background-color: #c8e6c9 !important; color: #2e7d32 !important; font-weight: 600;}
    </style>
""", unsafe_allow_html=True)

# --- Logo ---
futuristic_logo_svg = """
<svg width="72" height="72" viewBox="0 0 72 72" fill="none">
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
"""
st.markdown(f'<div class="futuristic-logo">{futuristic_logo_svg}</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🌾 Terrคi: The Futuristic AI Farming Guide</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Empowering Indian farmers with AI, real-time insights, and smart agriculture innovations</div>', unsafe_allow_html=True)

def is_meta_query(q):
    meta_keywords = ["who are you", "created", "your name", "developer", "model", "prudhvi", "about you"]
    return any(kw in q.lower() for kw in meta_keywords)

def handle_meta_query():
    return (
        "🤖 I am Terrคi, developed by Prudhvi, an engineer passionate about Indian agriculture. "
        "My mission is to empower Indian farmers with practical, region-specific guidance for every stage of cultivation, "
        "combining AI with real-time knowledge and innovation."
    )

def get_rag_answer(question, image_bytes=None, image_filename=None):
    tavily_result = tavily_search.invoke({"query": question})
    image_base64 = None
    if image_bytes:
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    # Prompt with image context
    system_prompt = (
        "You are an expert Indian agricultural advisor AI. "
        "You are given a user's question and a set of search results from trusted Indian sources."
        "\n\nIf the user has uploaded an image, analyze it carefully:"
        "\n- If it is a plant, assess its health, explain your reasoning, and if healthy, suggest fertilizers and growth techniques; if unhealthy, suggest fertilizers and precautions to restore health."
        "\n- If it is fertilizer, soil, or any other farming-related image, explain what the image shows, its uses, and where/when to use it."
        "\n- If you cannot identify the image, say so politely and suggest how to get more help."
        "\n\nYour answer should be in this structure:"
        "\n- **Image Analysis:** (if image provided) What is in the image and your assessment."
        "\n- **Summary:** A direct answer to the user's question."
        "\n- **Step-by-step Solution:** Detailed, region-specific, actionable advice."
        "\n- **Confidence Level:** High/Medium/Low, based on search result quality and image clarity."
        "\n- **Suggested Next Steps:** If the answer is incomplete, suggest where to get more info (e.g., local agri office, helpline, etc.)."
        "\n\nHere are the search results:\n"
        f"{tavily_result}"
        "\n\nUser Question:\n"
        f"{question}"
        "\n\nDo NOT mention specific sources or web links in your answer. Use clear, simple language."
    )
    messages = [SystemMessage(content=system_prompt)]
    if image_base64:
        messages.append(HumanMessage(content="Attached is an image uploaded by the user (base64-encoded). Please analyze it as per the instructions.", additional_kwargs={"image_base64": image_base64, "filename": image_filename}))
    else:
        messages.append(HumanMessage(content=question))
    response = llm.invoke(messages)
    answer = response.content.strip()
    return answer

def get_self_qa(question):
    prompt = (
        "Given this user question about Indian farming, generate 2-3 related follow-up questions a farmer might ask. "
        "For each, give a detailed, region-specific answer. "
        "If possible, include local crop varieties, climate, and sustainable practices. "
        "Format:\nQ1: ...\nA1: ...\nQ2: ...\nA2: ...\n"
        f"User question: {question}"
    )
    messages = [
        SystemMessage(content="You are a helpful Indian farming assistant."),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages)
    return response.content.strip()

# --- Chat Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Image uploader ---
uploaded_file = st.file_uploader("Attach a plant, fertilizer, soil, or farming image (optional)", type=["png", "jpg", "jpeg"])
image_bytes = None
image_filename = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded image", use_column_width=True)
    uploaded_file.seek(0)
    image_bytes = uploaded_file.read()
    image_filename = uploaded_file.name

prompt = st.chat_input("Ask about farming, soil, pests, irrigation, or anything in Indian agriculture…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        if uploaded_file is not None:
            st.image(image, caption="Your uploaded image", use_column_width=True)

    with st.chat_message("assistant"):
        if is_meta_query(prompt):
            response = handle_meta_query()
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            with st.spinner("Consulting AI experts..."):
                rag_answer = get_rag_answer(prompt, image_bytes=image_bytes, image_filename=image_filename)
                st.markdown(rag_answer)
                self_qa = get_self_qa(prompt)
                st.markdown("---\n**Other questions you may have:**")
                st.markdown(self_qa)
                st.session_state.messages.append({"role": "assistant", "content": rag_answer + "\n\n" + self_qa})

st.markdown(
    "<div style='text-align:center; color:#888888; margin-top:3rem; font-size:0.9rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi & AI • May 2025"
    "</div>",
    unsafe_allow_html=True
)
