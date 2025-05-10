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

# --- CSS and HTML for search bar with paperclip icon ---
st.markdown("""
<style>
  .search-container {
    position: relative;
    width: 100%;
    max-width: 720px;
    margin: auto;
  }
  input#search-input {
    width: 100%;
    padding: 12px 48px 12px 16px; /* space for icon on right */
    font-size: 1.1rem;
    border: 2px solid #81c784;
    border-radius: 12px;
    outline: none;
    color: #2e7d32;
    background-color: #f1f8e9;
  }
  input#search-input:focus {
    border-color: #4caf50;
    box-shadow: 0 0 8px #a5d6a7;
  }
  #file-upload {
    display: none;
  }
  label[for="file-upload"] {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    cursor: pointer;
    font-size: 1.4rem;
    color: #4caf50;
    user-select: none;
  }
  label[for="file-upload"]:hover {
    color: #388e3c;
  }
</style>

<div class="search-container">
  <input type="text" id="search-input" placeholder="Ask about farming, soil, pests, irrigation, or anything in Indian agriculture…" />
  <label for="file-upload" title="Attach an image">📎</label>
  <input type="file" id="file-upload" accept="image/png, image/jpeg" />
</div>

<script>
  const input = document.getElementById('search-input');
  const fileInput = document.getElementById('file-upload');

  // When user selects a file, send event to Streamlit
  fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function(e) {
        const base64 = e.target.result.split(',')[1];
        // Send file name and base64 to Streamlit via window.parent.postMessage
        window.parent.postMessage({func: 'fileUpload', name: file.name, data: base64}, '*');
      };
      reader.readAsDataURL(file);
    }
  });

  // Send input value to Streamlit on Enter key
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      window.parent.postMessage({func: 'queryInput', query: input.value}, '*');
    }
  });
</script>
""", unsafe_allow_html=True)

# --- Streamlit side: receive JS messages via st.experimental_get_query_params hack ---

# We'll use Streamlit's experimental features to capture JS messages.
# Since Streamlit doesn't support direct JS->Python messaging, we simulate with st.session_state

if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if "user_query" not in st.session_state:
    st.session_state.user_query = ""

# Helper to decode base64 to bytes
def base64_to_bytes(b64string):
    import base64
    return base64.b64decode(b64string)

# We cannot directly receive JS messages, so as a workaround,
# provide a manual file uploader fallback below (or use streamlit components in advanced setups).

# Manual fallback for file upload and query input:
st.markdown("### Or use the inputs below if the above bar doesn't work:")

user_query = st.text_input("Your question:", value=st.session_state.user_query)
uploaded_file = st.file_uploader("Attach an image (plant, fertilizer, soil, etc.)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.session_state.uploaded_file_data = uploaded_file.read()
    st.session_state.uploaded_file_name = uploaded_file.name
else:
    st.session_state.uploaded_file_data = None
    st.session_state.uploaded_file_name = None

if user_query:
    st.session_state.user_query = user_query

# --- Your existing chatbot logic below ---
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

# --- Chat session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Submit button ---
if st.button("Submit Query"):
    if not st.session_state.user_query and not st.session_state.uploaded_file_data:
        st.warning("Please enter a question or upload an image.")
    else:
        user_query = st.session_state.user_query
        image_bytes = st.session_state.uploaded_file_data
        image_filename = st.session_state.uploaded_file_name

        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)
            if image_bytes:
                st.image(image_bytes, caption="Your uploaded image", use_column_width=True)

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

# --- Footer ---
st.markdown(
    "<div style='text-align:center; color:#888888; margin-top:3rem; font-size:0.9rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi & AI • May 2025"
    "</div>",
    unsafe_allow_html=True
)
