import os
import random
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage

# --- ENV & API ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)
tavily_search = TavilySearch(api_key=TAVILY_API_KEY, max_results=3)

# --- LOGO & THEME ---
futuristic_logo_svg = """<svg width="72" height="72" viewBox="0 0 72 72" fill="none">
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
</svg>"""

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap');
        .stApp { background-color: #ffffff; color: #333333; font-family: 'Montserrat', sans-serif; }
        .futuristic-logo { display: flex; justify-content: center; align-items: center; margin-bottom: -6px; }
        .main-title { text-align: center; color: #4caf50; font-size: 2.8rem; font-weight: 700; letter-spacing: 1.2px; margin-bottom: 0.3rem; }
        .subtitle { text-align: center; color: #666666; font-size: 1.25rem; margin-bottom: 2rem; font-weight: 500; }
        .stChatInput input { font-size: 1.1rem !important; background: #f1f8e9; border: 2px solid #81c784; border-radius: 12px; color: #2e7d32; padding-left: 14px; height: 40px; transition: border-color 0.3s ease; }
        .stChatInput input:focus { border-color: #4caf50 !important; outline: none; box-shadow: 0 0 8px #a5d6a7; }
        .stButton>button { background-color: #4caf50; color: #ffffff; font-weight: 700; border-radius: 12px; padding: 10px 24px; border: none; box-shadow: 0 4px 12px #81c784aa; transition: background-color 0.3s ease; }
        .stButton>button:hover { background-color: #388e3c; box-shadow: 0 6px 16px #66bb6aaa; cursor: pointer; }
        .stMarkdown { background-color: #f9fbe7; border-radius: 14px; padding: 22px; margin-bottom: 20px; box-shadow: 0 3px 15px #c5e1a5aa; color: #2e7d32 !important; font-size: 1.05rem; line-height: 1.6; }
        .stChatMessage > div { background-color: #e8f5e9 !important; border-radius: 14px !important; color: #1b5e20 !important; padding: 14px !important; font-size: 1rem !important; line-height: 1.5 !important; box-shadow: 0 1px 6px #a5d6a7aa; }
        .stChatMessage.stChatMessage-user > div { background-color: #c8e6c9 !important; color: #2e7d32 !important; font-weight: 600; }
        hr { border: none; border-top: 1px solid #a5d6a7; margin: 24px 0; }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-thumb { background-color: #81c784; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

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

# --- Diverse RAG Prompt Templates ---
rag_templates = [
    # Template 1: Structured, source-citing
    """You are an expert Indian agricultural advisor AI. You are given a user's question and a set of search results from trusted Indian sources.

    Your job is to:
    1. Read the search results and extract the most relevant facts.
    2. Prefer facts and advice from the search results. If you use information from a search result, cite it as [Source 1], [Source 2], etc.
    3. If the search results are incomplete, use your own expertise but clearly say so.
    4. Structure your answer as follows:
       - **Summary:** A quick answer to the user's question.
       - **Step-by-step Solution:** Detailed, region-specific, actionable advice.
       - **Sources Used:** List which search results you used.
       - **Confidence Level:** High/Medium/Low, based on search result quality.
       - **Suggested Next Steps:** If the answer is incomplete, suggest where the user can get more info (e.g., local agri office, helpline, etc.).

    Here are the search results (label them as [Source 1], [Source 2], ...):
    {tavily_text}

    User Question:
    {question}

    Now answer as per the structure above. Use clear, simple language.
    """,

    # Template 2: Conversational, practical, local focus
    """You are a friendly Indian farming assistant AI. You have access to the latest web search results from trusted Indian agricultural sources.

    Please:
    - Read the search results and pick out the most useful, practical tips.
    - Where possible, include local crop varieties, climate, and practices.
    - If you use info from a search result, mention it as [Source 1], [Source 2], etc.
    - If search results are missing details, use your own expertise and say so.
    - Write your answer in a conversational, easy-to-understand style, as if talking to a farmer.

    Search results:
    {tavily_text}

    Farmer's question:
    {question}

    Give your best answer below:
    """,

    # Template 3: Step-by-step, actionable, with risk warnings
    """You are an Indian agriculture expert AI. Below are search results from reliable Indian sources.

    Please:
    - Extract the most important facts and steps from the search results.
    - Write a step-by-step guide for the farmer, including any risks or warnings.
    - Cite sources as [Source 1], [Source 2], etc.
    - If you need to use your own expertise, mention it.

    Search results:
    {tavily_text}

    Farmer's question:
    {question}

    Provide a step-by-step answer, and highlight any risks or precautions.
    """,

    # Template 4: Table format, with summary and details
    """You are an Indian agriculture AI advisor. You have access to web search results from Indian agri sources.

    Please:
    - Summarize the answer in 2-3 lines.
    - Then provide a table with key facts, steps, or recommendations.
    - Cite sources as [Source 1], [Source 2], etc.
    - If search results are missing info, use your expertise and say so.

    Search results:
    {tavily_text}

    Farmer's question:
    {question}

    Answer with a summary and a table:
    """
]

def get_rag_answer(question):
    tavily_result = tavily_search.invoke({"query": question})
    if isinstance(tavily_result, dict) and 'results' in tavily_result:
        search_snippets = tavily_result['results']
        tavily_text = "\n".join([f"[Source {i+1}] {res.get('title','')}: {res.get('snippet','')}" for i, res in enumerate(search_snippets)])
    else:
        search_snippets = []
        tavily_text = str(tavily_result)

    # Pick a random RAG prompt template for variety
    template = random.choice(rag_templates)
    system_prompt = template.format(tavily_text=tavily_text, question=question)
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

# --- Show Top Search Snippets as Cards ---
def show_search_snippets(search_snippets):
    if search_snippets:
        st.markdown("#### 🔎 Top Search Results")
        for i, res in enumerate(search_snippets[:3]):
            st.markdown(
                f"""
                <div style="background:#e8f5e9; border-radius:12px; padding:16px; margin-bottom:12px; box-shadow: 0 2px 8px #a5d6a7;">
                    <b>[Source {i+1}] {res.get('title','')}</b><br>
                    <span style="color:#388e3c;">{res.get('snippet','')}</span>
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
                show_search_snippets(search_snippets)
                st.markdown("---\n**Other questions you may have:**")
                self_qa = get_self_qa(prompt)
                st.markdown(self_qa)
                st.session_state.messages.append({"role": "assistant", "content": rag_answer + "\n\n" + self_qa})

# --- Footer ---
st.markdown(
    "<div style='text-align:center; color:#888888; margin-top:3rem; font-size:0.9rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi & AI • May 2025"
    "</div>",
    unsafe_allow_html=True
)
