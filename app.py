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
  <path d="M36 54 L36 68" stroke="#00bfae" stroke-width="2"/>
  <circle cx="36" cy="68" r="2.5" fill="#00bfae"/>
  <path d="M41 44 L53 51" stroke="#00bfae" stroke-width="2"/>
  <circle cx="53" cy="51" r="2.2" fill="#00bfae"/>
  <path d="M31 44 L19 51" stroke="#00bfae" stroke-width="2"/>
  <circle cx="19" cy="51" r="2.2" fill="#00bfae"/>
  <circle cx="36" cy="14" r="3" fill="#00e676" stroke="#1de9b6" stroke-width="1"/>
  <text x="36" y="15.5" font-size="2.5" text-anchor="middle" fill="#232526" font-family="Orbitron">AI</text>
</svg>
"""

# --- Advanced Theme ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
        .stApp {
            background: linear-gradient(135deg, #121212 0%, #1e1e1e 100%);
            color: #e0e0e0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .futuristic-logo {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: -8px;
        }
        .main-title {
            text-align: center;
            color: #4caf50;
            font-size: 2.7rem;
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            letter-spacing: 1.5px;
            text-shadow: 0 0 10px #4caf50, 0 0 40px #81c784aa;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            text-align: center;
            color: #a5d6a7;
            font-size: 1.2rem;
            margin-bottom: 2rem;
            font-family: 'Orbitron', sans-serif;
        }
        .stChatInput input {
            font-size: 1.1rem !important;
            background: #2e7d32;
            border: 1px solid #4caf50;
            border-radius: 8px;
            color: #e0e0e0;
            padding-left: 12px;
        }
        .stButton>button {
            background: linear-gradient(90deg, #4caf50 0%, #81c784 100%);
            color: #121212;
            font-weight: 700;
            border-radius: 8px;
            box-shadow: 0 2px 8px #388e3caa;
            transition: background 0.3s ease;
        }
        .stButton>button:hover {
            background: linear-gradient(90deg, #81c784 0%, #4caf50 100%);
        }
        .stMarkdown {
            background: #212121;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 24px #388e3caa;
            color: #e0e0e0 !important;
            font-size: 1rem;
            line-height: 1.5;
        }
        .stChatMessage > div {
            background-color: #2e7d32 !important;
            border-radius: 12px !important;
            color: #e0e0e0 !important;
            padding: 12px !important;
            font-size: 1rem !important;
            line-height: 1.4 !important;
        }
        .stChatMessage.stChatMessage-user > div {
            background-color: #1b5e20 !important;
            color: #c8e6c9 !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
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

# --- Advanced RAG Function ---
def get_rag_answer(question):
    tavily_result = tavily_search.invoke({"query": question})
    # If Tavily returns a dict with 'results', extract the list for snippet cards
    search_snippets = []
    if isinstance(tavily_result, dict) and 'results' in tavily_result:
        search_snippets = tavily_result['results']
        tavily_text = "\n".join([f"[Source {i+1}] {res.get('title','')}: {res.get('snippet','')}" for i, res in enumerate(search_snippets)])
    else:
        tavily_text = str(tavily_result)
    # Advanced, explicit system prompt
    system_prompt = (
        "You are an expert Indian agricultural advisor AI. "
        "You are given a user's question and a set of search results from trusted Indian sources."
        "\n\nYour job is to:"
        "\n1. Read the search results and extract the most relevant facts."
        "\n2. Prefer facts and advice from the search results. If you use information from a search result, cite it as [Source 1], [Source 2], etc."
        "\n3. If the search results are incomplete, use your own expertise but clearly say so."
        "\n4. Structure your answer as follows:"
        "\n   - **Summary:** A quick answer to the user's question."
        "\n   - **Step-by-step Solution:** Detailed, region-specific, actionable advice."
        "\n   - **Sources Used:** List which search results you used."
        "\n   - **Confidence Level:** High/Medium/Low, based on search result quality."
        "\n   - **Suggested Next Steps:** If the answer is incomplete, suggest where the user can get more info (e.g., local agri office, helpline, etc.)."
        "\n\nHere are the search results (label them as [Source 1], [Source 2], ...):"
        f"\n{tavily_text}"
        "\n\nUser Question:"
        f"\n{question}"
        "\n\nNow answer as per the structure above. Use clear, simple language."
    )
    messages = [SystemMessage(content=system_prompt)]
    response = llm.invoke(messages)
    answer = response.content.strip()
    combined = f"{answer}\n\n---\n**Top Search Results:**\n{tavily_text}"
    return combined, search_snippets

# --- Self Q&A with Richer Prompts ---
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

# --- Optional: Show Top Search Snippets as Cards ---
def show_search_snippets(search_snippets):
    if search_snippets:
        st.markdown("#### 🔎 Top Search Results")
        for i, res in enumerate(search_snippets[:3]):
            st.markdown(
                f"""
                <div style="background:#263238; border-radius:8px; padding:12px; margin-bottom:8px;">
                    <b>[Source {i+1}] {res.get('title','')}</b><br>
                    <span style="color:#b2dfdb;">{res.get('snippet','')}</span>
                </div>
                """, unsafe_allow_html=True
            )

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
        else:
            with st.spinner("Consulting AI experts and searching the latest info..."):
                rag_answer, search_snippets = get_rag_answer(prompt)
                st.markdown(rag_answer)
                show_search_snippets(search_snippets)  # Optional: show snippet cards
                st.markdown("---\n**Other questions you may have:**")
                self_qa = get_self_qa(prompt)
                st.markdown(self_qa)
                st.session_state.messages.append({"role": "assistant", "content": rag_answer + "\n\n" + self_qa})

st.markdown(
    "<div style='text-align:center; color:#9e9e9e; margin-top:2rem; font-size:0.9rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi & AI • May 2025"
    "</div>",
    unsafe_allow_html=True
)
