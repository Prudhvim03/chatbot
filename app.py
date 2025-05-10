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

# --- Futuristic AI-Rice Logo (SVG) ---
futuristic_logo_svg = """
<svg width="72" height="72" viewBox="0 0 72 72" fill="none">
  <defs>
    <radialGradient id="glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#00e676" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="#1de9b6" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="stem" x1="36" y1="18" x2="36" y2="60" gradientUnits="userSpaceOnUse">
      <stop stop-color="#00e676"/>
      <stop offset="1" stop-color="#00bfae"/>
    </linearGradient>
  </defs>
  <ellipse cx="36" cy="54" rx="22" ry="10" fill="url(#glow)"/>
  <path d="M36 54 Q46 34 62 22 Q46 28 36 54" fill="#FFF176" opacity="0.92"/>
  <path d="M36 54 Q26 34 10 22 Q26 28 36 54" fill="#FFF176" opacity="0.92"/>
  <rect x="34" y="18" width="4" height="36" rx="2" fill="url(#stem)"/>
  <ellipse cx="36" cy="18" rx="7" ry="9" fill="#FFF176" stroke="#00e676" stroke-width="1.5"/>
  <!-- Circuit lines -->
  <path d="M36 54 L36 68" stroke="#00bfae" stroke-width="2"/>
  <circle cx="36" cy="68" r="2.5" fill="#00bfae"/>
  <path d="M41 44 L53 51" stroke="#00bfae" stroke-width="2"/>
  <circle cx="53" cy="51" r="2.2" fill="#00bfae"/>
  <path d="M31 44 L19 51" stroke="#00bfae" stroke-width="2"/>
  <circle cx="19" cy="51" r="2.2" fill="#00bfae"/>
  <!-- AI node -->
  <circle cx="36" cy="14" r="3" fill="#00e676" stroke="#1de9b6" stroke-width="1"/>
  <text x="36" y="15.5" font-size="2.5" text-anchor="middle" fill="#232526" font-family="Orbitron">AI</text>
</svg>
"""

# --- Advanced Futuristic Theme (CSS) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
        .stApp {
            background: linear-gradient(135deg, #232526 0%, #0f2027 100%);
            color: #e0f7fa;
        }
        .futuristic-logo {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: -8px;
        }
        .main-title {
            text-align: center;
            color: #00e676;
            font-size: 2.7rem;
            font-family: 'Orbitron', sans-serif;
            font-weight: bold;
            letter-spacing: 1.5px;
            text-shadow: 0 0 10px #00bfae, 0 0 40px #00bfae44;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            text-align: center;
            color: #b2dfdb;
            font-size: 1.1rem;
            margin-bottom: 2rem;
            font-family: 'Orbitron', sans-serif;
        }
        .stChatInput input {
            font-size: 1.1rem !important;
            background: rgba(0, 230, 118, 0.08);
            border: 1px solid #00e676;
            border-radius: 8px;
            color: #e0f7fa;
        }
        .stButton>button {
            background: linear-gradient(90deg, #00e676 0%, #1de9b6 100%);
            color: #232526;
            font-weight: bold;
            border-radius: 8px;
            box-shadow: 0 2px 8px #00bfae44;
        }
        .stMarkdown {
            background: rgba(35, 37, 38, 0.7);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 12px;
            box-shadow: 0 4px 24px #00bfae22;
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
        "🤖 I am Terrคi, developed by Prudhvi, an engineer passionate about Indian agriculture. "
        "My mission is to empower Indian farmers with practical, region-specific guidance for every stage of cultivation, "
        "combining AI with real-time knowledge and innovation."
    )

# --- RAG Answer Function ---
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
    combined = f"**AI Guidance:**\n{answer}\n\n**Latest Insights:**\n{tavily_result}"
    return combined

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
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        if is_meta_query(prompt):
            response = handle_meta_query()
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            with st.spinner("Consulting AI experts and searching the latest info..."):
                rag_answer = get_rag_answer(prompt)
                st.markdown(rag_answer)
                # Self-questions and answers
                st.markdown("---\n**Other questions you may have:**")
                self_qa = get_self_qa(prompt)
                st.markdown(self_qa)
                st.session_state.messages.append({"role": "assistant", "content": rag_answer + "\n\n" + self_qa})

# --- Footer ---
st.markdown(
    "<div style='text-align:center; color:#607d8b; margin-top:2rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi • May 2025"
    "</div>",
    unsafe_allow_html=True
)
