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

# Unique South Indian rice farming icon (SVG)
rice_icon_svg = """
<svg width="48" height="48" viewBox="0 0 48 48" fill="none">
  <ellipse cx="24" cy="38" rx="16" ry="6" fill="#9CCC65"/>
  <path d="M24 38 Q28 25 38 18 Q28 20 24 38" fill="#FFF176"/>
  <path d="M24 38 Q20 25 10 18 Q20 20 24 38" fill="#FFF176"/>
  <rect x="22" y="10" width="4" height="28" rx="2" fill="#8D6E63"/>
  <ellipse cx="24" cy="10" rx="4" ry="6" fill="#FFF176"/>
</svg>
"""

# South Indian theme colors
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #f4fce3 0%, #e8f5e9 100%);
        }
        .rice-icon {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: -10px;
        }
        .main-title {
            text-align: center;
            color: #388e3c;
            font-size: 2.5rem;
            font-family: 'Noto Serif', serif;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            text-align: center;
            color: #795548;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        .stChatInput input {
            font-size: 1.1rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# Header with icon and title
st.markdown(f'<div class="rice-icon">{rice_icon_svg}</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🌾 AI Agricultural Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Expert guidance for Indian farmers - AI & real-time knowledge</div>', unsafe_allow_html=True)

# Meta-question detection
def is_meta_query(q):
    meta_keywords = ["who are you", "created", "your name", "developer", "model", "prudhvi", "about you"]
    return any(kw in q.lower() for kw in meta_keywords)

def handle_meta_query():
    return (
        "🌱 I was developed by Prudhvi, an engineer passionate about Indian agriculture and farming. "
        "My mission is to empower  Indian farmers with practical, region-specific guidance for every stage of  cultivation."
    )

def get_rag_answer(question):
    # System prompt tailored for Indian/South Indian rice farming
    system_prompt = (
        "You are a Indian agricultural expert specializing in farming. "
        "Give practical, region-specific, step-by-step advice using both your knowledge and the latest information from trusted Indian agricultural sources. "
        "Always explain in clear, simple language. If possible, mention local varieties, climate, and sustainable practices. "
        "If you don't know, say so and suggest how to find out."
    )
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ]
    # LLM answer
    response = llm.invoke(messages)
    answer = response.content.strip()
    # Retrieve supporting info via Tavily
    tavily_result = tavily_search.invoke({"query": question})
    # Combine LLM and search
    combined = f"**AI Guidance:**\n{answer}\n\n**Latest Insights :**\n{tavily_result}"
    return combined

def get_self_qa(question):
    # Prompt LLM to generate self-questions and answers
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

# Chat session state
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask your question on farming, soil, pests, irrigation, or anything Indian agriculture…")

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
            with st.spinner("Consulting experts and searching the latest info..."):
                rag_answer = get_rag_answer(prompt)
                st.markdown(rag_answer)
                # Self-questions and answers
                st.markdown("---\n**Other questions you may have:**")
                self_qa = get_self_qa(prompt)
                st.markdown(self_qa)
                st.session_state.messages.append({"role": "assistant", "content": rag_answer + "\n\n" + self_qa})

# Footer
st.markdown(
    "<div style='text-align:center; color:#607d8b; margin-top:2rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi & AI • May 2025"
    "</div>",
    unsafe_allow_html=True
)
