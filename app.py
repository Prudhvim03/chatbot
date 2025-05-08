import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from tavily import TavilyClient
import os
import time

# --- SET API KEYS ---
os.environ["GROQ_API_KEY"] = "YOUR_GROQ_API_KEY"  # Replace with your Groq API key
os.environ["TAVILY_API_KEY"] = "YOUR_TAVILY_API_KEY"  # Replace with your Tavily API key

# --- FARMING KNOWLEDGE BASE ---
documents = [
    "Maize requires well-drained soil and regular watering.",
    "Rice thrives in flooded fields and warm climates.",
    "Use organic compost to improve soil fertility.",
    "Monitor crop health using remote sensors for early pest detection.",
    "Crop rotation helps maintain soil health and reduce pests.",
    "Drip irrigation conserves water and improves crop yields.",
]

# --- SET UP CHROMADB VECTOR STORE ---
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma.from_texts(documents, embeddings)
retriever = vectorstore.as_retriever()

# --- SET UP LLM AND RAG PIPELINE ---
llm = ChatGroq(model_name="llama3-70b-8192")  # Free tier model
prompt = ChatPromptTemplate.from_template(
    "You are an expert farming assistant. Use the following context to answer the user's question."
    "\n\nContext: {context}"
    "\nQuestion: {question}"
    "\nAnswer:"
)
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
)

# --- TAVILY CLIENT FOR REFERENCES ---
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def get_references(query, max_results=3):
    try:
        response = tavily.search(query=query, search_depth="advanced")
        refs = []
        for r in response.get("results", [])[:max_results]:
            refs.append({
                "title": r["title"],
                "url": r["url"],
                "snippet": r["content"][:200] + "..."
            })
        return refs
    except Exception:
        return []

# --- STREAMLIT UI ---
st.set_page_config(page_title="🌾 Farming Solutions Chatbot", layout="wide")
st.title("🌾 Farming Solutions Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Ask your farming question here..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate bot response (simulate streaming)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        # Call RAG chain
        response = rag_chain.invoke(prompt)
        answer = response.content.strip()

        # Display response word by word
        for word in answer.split():
            full_response += word + " "
            placeholder.markdown(full_response + "▌")
            time.sleep(0.03)
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Fetch and display references
    references = get_references(prompt)
    if references:
        st.markdown("### 🔗 References")
        for ref in references:
            st.markdown(f"- [{ref['title']}]({ref['url']})  \n{ref['snippet']}")
