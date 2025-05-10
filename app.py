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

llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)
tavily_search = TavilySearch(api_key=TAVILY_API_KEY, max_results=3)

# --- (UI, SVG, CSS, Header code as in your file) ---

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

# --- Advanced RAG Function (no Top Search Results, no snippet cards) ---
def get_rag_answer(question):
    tavily_result = tavily_search.invoke({"query": question})

    if isinstance(tavily_result, dict) and 'results' in tavily_result:
        search_snippets = tavily_result['results']
        tavily_text = "\n".join([f"[Source {i+1}] {res.get('title','')}: {res.get('snippet','')}" for i, res in enumerate(search_snippets)])
    else:
        search_snippets = []
        tavily_text = str(tavily_result)

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
    return answer, search_snippets

# --- Detect if user is asking for "other questions" ---
def is_selfqa_query(q):
    triggers = [
        "other questions",
        "more questions",
        "what else",
        "related questions",
        "suggest more",
        "show more",
        "what else can i ask",
        "give me more questions"
    ]
    q_lower = q.strip().lower()
    return any(trigger in q_lower for trigger in triggers)

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
            # Only show self Q&A if user asks for it
            if len(st.session_state.messages) > 1:
                # Use the previous user question for generating self Q&A
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
        else:
            with st.spinner("Consulting AI experts and searching the latest info..."):
                rag_answer, _ = get_rag_answer(prompt)
                st.markdown(rag_answer)
                st.session_state.messages.append({"role": "assistant", "content": rag_answer})

# --- Footer (unchanged) ---
st.markdown(
    "<div style='text-align:center; color:#888888; margin-top:3rem; font-size:0.9rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi & AI • May 2025"
    "</div>",
    unsafe_allow_html=True
)
