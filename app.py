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

# --- Theme and Layout CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap');
        .stApp {background: #f9fafb; color: #232526; font-family: 'Montserrat', sans-serif;}
        .centered-header {text-align:center; color:#222; font-size:2.5rem; font-weight:700; margin:2.5rem 0 1.5rem 0;}
        .subtitle {text-align:center; color:#4caf50; font-size:1.2rem; margin-bottom:2.5rem;}
        .perplexity-bar {display: flex; align-items: center; background: #fff; border-radius: 18px; border: 2px solid #e0e0e0; box-shadow: 0 2px 12px #a5d6a733; padding: 0.25rem 1.2rem; max-width: 540px; margin: 0 auto 2.5rem auto;}
        .perplexity-bar .stTextInput>div>div>input {font-size: 1.25rem; background: transparent; border: none; color: #2e7d32; padding: 14px 8px;}
        .perplexity-bar .stTextInput>div>div>input:focus {outline: none;}
        .perplexity-bar .stFileUploader {margin-bottom: 0;}
        .perplexity-bar .stFileUploader label span {font-size: 1.7rem !important; color: #4caf50 !important; cursor: pointer; margin-left: -1.5rem;}
        .perplexity-bar .stFileUploader label span:hover {color: #388e3c !important;}
        .stButton>button {background-color: #4caf50; color: #fff; font-weight: 700; border-radius: 12px; padding: 10px 24px; border: none;}
        .stButton>button:hover {background-color: #388e3c;}
        .stMarkdown {background-color: #f9fbe7; border-radius: 14px; padding: 22px; margin-bottom: 20px; color: #2e7d32 !important;}
        .stChatMessage > div {background-color: #e8f5e9 !important; border-radius: 14px !important; color: #1b5e20 !important; padding: 14px !important;}
        .stChatMessage.stChatMessage-user > div {background-color: #c8e6c9 !important; color: #2e7d32 !important; font-weight: 600;}
        .uploaded-img-preview {display: flex; justify-content: center; margin-top: 1rem;}
    </style>
""", unsafe_allow_html=True)

# --- Centered Question Header ---
st.markdown('<div class="centered-header">What do you want to know?</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask about farming, soil, pests, irrigation, or anything in Indian agriculture. Attach an image if you wish!</div>', unsafe_allow_html=True)

# --- Perplexity-style search bar: text + paperclip in one row ---
with st.container():
    st.markdown('<div class="perplexity-bar">', unsafe_allow_html=True)
    col1, col2 = st.columns([8, 1])
    with col1:
        user_query = st.text_input(
            "", key="query", label_visibility="collapsed", placeholder="Ask anything..."
        )
    with col2:
        uploaded_file = st.file_uploader(
            "", type=["png", "jpg", "jpeg"], label_visibility="collapsed", accept_multiple_files=False
        )
        st.markdown(
            '<label for="perplexity-clip" style="position:absolute;top:12px;right:20px;cursor:pointer;font-size:1.7rem;color:#4caf50;">📎</label>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

image_bytes = None
image_filename = None
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Attached image", use_column_width=True)
    uploaded_file.seek(0)
    image_bytes = uploaded_file.read()
    image_filename = uploaded_file.name

# --- Chatbot logic ---
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
    system_prompt = (
        "You are an expert Indian agricultural advisor AI. "
        "You are given a user's question and a set of search results from trusted Indian sources."
        "\n\nIf the user has uploaded an image, analyze it carefully:"
        "\n- If it is a plant, determine if it is healthy or unhealthy. If healthy, explain why and suggest best fertilizers and modern techniques to improve growth. "
        "If unhealthy, explain the problems you see, suggest specific fertilizers, treatments, and precautions to restore health."
        "\n- If it is fertilizer, soil, or any other farming-related image, explain what it is, its uses, and where/when to use it for best results."
        "\n- If you cannot identify the image, say so politely and suggest how to get more help."
        "\n\nYour answer must follow this structure:"
        "\n1. **Image Analysis:** (if image provided) What is in the image and your assessment."
        "\n2. **Summary:** A direct, concise answer to the user's question."
        "\n3. **Step-by-step Solution:** Detailed, region-specific, actionable advice."
        "\n4. **Confidence Level:** High/Medium/Low, based on search result quality and image clarity."
        "\n5. **Suggested Next Steps:** If the answer is incomplete, suggest where to get more info (e.g., local agri office, helpline, etc.)."
        "\n\nHere are the search results:\n"
        f"{tavily_result}"
        "\n\nUser Question:\n"
        f"{question}"
        "\n\nDo NOT mention specific sources or web links in your answer. Use clear, simple language."
    )
    messages = [SystemMessage(content=system_prompt)]
    if image_base64:
        messages.append(HumanMessage(
            content="Attached is an image uploaded by the user (base64-encoded). Please analyze it as per the instructions.",
            additional_kwargs={"image_base64": image_base64, "filename": image_filename}
        ))
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

if st.button("Submit", use_container_width=True):
    if user_query.strip() == "" and not uploaded_file:
        st.warning("Please enter a question or upload an image.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
            if uploaded_file is not None:
                st.image(image, caption="Your uploaded image", use_column_width=True)

        with st.chat_message("assistant"):
            if is_meta_query(user_query):
                response = handle_meta_query()
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                with st.spinner("Consulting AI experts..."):
                    rag_answer = get_rag_answer(user_query, image_bytes=image_bytes, image_filename=image_filename)
                    st.markdown(rag_answer)
                    self_qa = get_self_qa(user_query)
                    st.markdown("---\n**Other questions you may have:**")
                    st.markdown(self_qa)
                    st.session_state.messages.append({"role": "assistant", "content": rag_answer + "\n\n" + self_qa})

st.markdown(
    "<div style='text-align:center; color:#888888; margin-top:3rem; font-size:0.9rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi & AI • May 2025"
    "</div>",
    unsafe_allow_html=True
)
