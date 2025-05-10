import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Set up LLM and Tavily Search
llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)
tavily_search = TavilySearch(api_key=TAVILY_API_KEY, max_results=3)

# --- Futuristic Agri-Tech Logo (SVG, farming colors) ---
futuristic_logo_svg = """
<svg width="72" height="72" viewBox="0 0 72 72" fill="none">
  <defs>
    <radialGradient id="soil" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#a1887f" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#fffde7" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="stem" x1="36" y1="18" x2="36" y2="60" gradientUnits="userSpaceOnUse">
      <stop stop-color="#689f38"/>
      <stop offset="1" stop-color="#388e3c"/>
    </linearGradient>
    <linearGradient id="grain" x1="0" y1="0" x2="0" y2="18" gradientUnits="userSpaceOnUse">
      <stop stop-color="#ffe082"/>
      <stop offset="1" stop-color="#fbc02d"/>
    </linearGradient>
  </defs>
  <ellipse cx="36" cy="54" rx="22" ry="10" fill="url(#soil)"/>
  <path d="M36 54 Q46 34 62 22 Q46 28 36 54" fill="#ffe082" opacity="0.92"/>
  <path d="M36 54 Q26 34 10 22 Q26 28 36 54" fill="#ffe082" opacity="0.92"/>
  <rect x="34" y="18" width="4" height="36" rx="2" fill="url(#stem)"/>
  <ellipse cx="36" cy="18" rx="7" ry="9" fill="url(#grain)" stroke="#fbc02d" stroke-width="1.5"/>
  <!-- Circuit lines -->
  <path d="M36 54 L36 68" stroke="#8d6e63" stroke-width="2"/>
  <circle cx="36" cy="68" r="2.5" fill="#8d6e63"/>
  <path d="M41 44 L53 51" stroke="#8d6e63" stroke-width="2"/>
  <circle cx="53" cy="51" r="2.2" fill="#8d6e63"/>
  <path d="M31 44 L19 51" stroke="#8d6e63" stroke-width="2"/>
  <circle cx="19" cy="51" r="2.2" fill="#8d6e63"/>
  <!-- AI node -->
  <circle cx="36" cy="14" r="3" fill="#fbc02d" stroke="#ffe082" stroke-width="1"/>
  <text x="36" y="15.5" font-size="2.5" text-anchor="middle" fill="#388e3c" font-family="Orbitron">AI</text>
</svg>
"""

# --- Farming Color Palette & Theme (CSS) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
        .stApp {
            background: linear-gradient(135deg, #fffde7 0%, #e8f5e9 100%);
            color: #37474f;
        }
        .futuristic-logo {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: -8px;
        }
        .main-title {
            text-align: center;
            color: #689f38;
            font-size: 2.7rem;
            font-family: 'Orbitron', sans-serif;
            font-weight: bold;
            letter-spacing: 1.5px;
            text-shadow: 0 0 10px #fbc02d, 0 0 40px #fbc02d44;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            text-align: center;
            color: #8d6e63;
            font-size: 1.1rem;
            margin-bottom: 2rem;
            font-family: 'Orbitron', sans-serif;
        }
        .stChatInput input {
            font-size: 1.1rem !important;
            background: rgba(255, 224, 130, 0.13);
            border: 1.5px solid #689f38;
            border-radius: 8px;
            color: #37474f;
        }
        .stButton>button {
            background: linear-gradient(90deg, #fbc02d 0%, #689f38 100%);
            color: #fffde7;
            font-weight: bold;
            border-radius: 8px;
            box-shadow: 0 2px 8px #8d6e6344;
        }
        .stMarkdown {
            background: rgba(232, 245, 233, 0.7);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 12px;
            box-shadow: 0 4px 24px #fbc02d22;
        }
        .stChatMessage > div {
            background: #fffde7 !important;
            border-radius: 12px !important;
            color: #37474f !important;
            padding: 16px !important;
            font-size: 1.07rem !important;
            line-height: 1.6 !important;
            box-shadow: 0 1px 8px #fbc02d22;
            margin-bottom: 10px;
            border: 1.5px solid #fbc02d44;
        }
        .stChatMessage.stChatMessage-user > div {
            background: #ffe082 !important;
            color: #689f38 !important;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header with Logo and Title ---
st.markdown(f'<div class="futuristic-logo">{futuristic_logo_svg}</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🌾 Terrคi: The Futuristic AI Farming Guide</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Empowering Indian farmers with AI, real-time insights, and smart agriculture innovations</div>', unsafe_allow_html=True)

# --- Meta-question detection ---
def is_meta_query(q):
    meta_keywords = ["who are you", "created", "your name", "developer", "model", "prudhvi", "about you"]
    return any(kw in q.lower() for kw in meta_keywords)

def handle_meta_query():
    return (
        " I am Terrคi, developed by Prudhvi, an engineer passionate about Indian agriculture. "
        "My mission is to empower Indian farmers, students, and agriculturalists with practical, region-specific guidance for every stage of cultivation, "
        "combining AI with real-time knowledge and innovation."
    )

# --- Only show self Q&A if user asks for it ---
def is_selfqa_query(q):
    triggers = [
        "other questions", "more questions", "what else", "related questions", "suggest more", "show more",
        "what else can i ask", "give me more questions"
    ]
    q_lower = q.strip().lower()
    return any(trigger in q_lower for trigger in triggers)

# --- Restrict to farming/agriculture/Agri-student questions ---
def is_farming_question(question):
    keywords = [
        "farm", "farmer", "agriculture", "crop", "soil", "irrigation", "weather",
        "pesticide", "fertilizer", "seed", "plant", "harvest", "yield", "agronomy",
        "horticulture", "animal husbandry", "disease", "pest", "organic", "sowing",
        "rain", "monsoon", "market price", "mandi", "tractor", "dairy", "farming",
        "agriculturist", "agriculturalist", "agri", "agronomist", "extension", "agri student",
        "agri career", "kisan", "polyhouse", "greenhouse", "micro irrigation", "crop insurance",
        "fpo", "farmer producer", "soil health", "farm loan", "krishi", "agriculture student"
    ]
    q = question.lower()
    return any(word in q for word in keywords)

# --- RAG Answer Function (no Top Search Results) ---
def get_rag_answer(question):
    system_prompt = (
        "You are an Indian agricultural expert specializing in farming. "
        "Give practical, region-specific, step-by-step advice using both your knowledge and the latest information from trusted Indian agricultural sources. "
        "Always explain in clear, simple language. If possible, mention local varieties, climate, and sustainable practices. "
        "If you don't know, say so and suggest how to find out."
    )
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ]
    response = llm.invoke(messages)
    answer = response.content.strip()
    tavily_result = tavily_search.invoke({"query": question})
    # Only include Tavily if it seems on-topic
    return f"**AI Guidance:**\n{answer}"

# --- Self Q&A Function ---
def get_self_qa(question):
    prompt = (
        "Given this user question about Indian farming, generate 2-3 related follow-up questions a farmer might ask, "
        "and answer each in detail, focusing on Indian context and practical steps. "
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

prompt = st.chat_input("Ask about farming, soil, pests, irrigation, or anything in Indian agriculture…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if is_meta_query(prompt):
            response = handle_meta_query()
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        elif is_selfqa_query(prompt):
            if len(st.session_state.messages) > 1:
                prev_user_msg = next((m["content"] for m in reversed(st.session_state.messages[:-1]) if m["role"] == "user"), None)
                if prev_user_msg:
                    st.markdown("**Other questions you may have:**")
                    self_qa = get_self_qa(prev_user_msg)
                    st.markdown(self_qa)
                    st.session_state.messages.append({"role": "assistant", "content": self_qa})
                else:
                    st.markdown("Please ask a farming question first, then I can suggest more questions.")
            else:
                st.markdown("Please ask a farming question first, then I can suggest more questions.")
        elif not is_farming_question(prompt):
            response = (
                "🙏 Sorry, I can only answer questions related to farming, agriculture, or agri-studies. "
                "If you are a farmer, student, or agriculturalist, please ask about crops, soil, weather, pest management, agri-careers, etc."
            )
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            with st.spinner("Consulting AI experts and searching the latest info..."):
                rag_answer = get_rag_answer(prompt)
                st.markdown(rag_answer)
                st.session_state.messages.append({"role": "assistant", "content": rag_answer})

# --- Footer ---
st.markdown(
    "<div style='text-align:center; color:#8d6e63; margin-top:2rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi • May 2025"
    "</div>",
    unsafe_allow_html=True
)
