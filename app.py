import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
import speech_recognition as sr
import pyttsx3
from PIL import Image
import easyocr
from tavily import TavilyClient
import os

# --- SET API KEYS ---
os.environ["GROQ_API_KEY"] = "YOUR_GROQ_API_KEY"  # Replace with your Groq API key
os.environ["TAVILY_API_KEY"] = "YOUR_TAVILY_API_KEY"  # Replace with your Tavily API key

# --- FARMING KNOWLEDGE BASE ---
documents = [
    "Maize needs well-drained soil. Water regularly.",
    "Rice grows best in flooded fields and warm weather.",
    "Use compost to improve soil fertility.",
    "Watch for pests using remote sensors."
]

# --- SET UP CHROMADB VECTOR STORE ---
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_texts(documents, embeddings)
retriever = vectorstore.as_retriever()

# --- SET UP LLM AND RAG PIPELINE ---
llm = ChatGroq(model_name="llama2-70b-4096")  # Or "mixtral-8x7b-32768", "llama3-70b-8192"
prompt = ChatPromptTemplate.from_template(
    "You are a farming expert. Use this context: {context}\nQuestion: {question}\nAnswer:"
)
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
)

# --- VOICE INPUT ---
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening... (Speak now)")
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except:
        return ""

# --- VOICE OUTPUT ---
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# --- OCR FOR IMAGE INPUT ---
def ocr_image(image):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image)
    return " ".join([res[1] for res in result])

# --- FETCH REFERENCES WITH TAVILY ---
def get_references(query):
    tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    response = tavily.search(query=query, search_depth="advanced")
    references = []
    for result in response["results"]:
        references.append({
            "title": result["title"],
            "url": result["url"],
            "content": result["content"][:200]  # Short summary
        })
    return references

# --- STREAMLIT UI ---
st.title("🌱 Farming Solutions Chatbot")

query = st.text_input("Ask your farming question or upload an image:")

if st.button("🎤 Voice Input"):
    query = listen()
    st.write(f"Voice input: {query}")

uploaded_image = st.file_uploader("Upload crop image for diagnosis", type=["png", "jpg", "jpeg"])
if uploaded_image:
    image = Image.open(uploaded_image)
    ocr_text = ocr_image(image)
    st.write(f"Extracted text: {ocr_text}")
    query = f"Detect crop problem from image: {ocr_text}"

if query:
    response = rag_chain.invoke(query)
    st.write("### Answer")
    st.write(response.content)
    speak(response.content)

    references = get_references(query)
    st.write("### References")
    if references:
        for ref in references:
            st.markdown(f"- **[{ref['title']}]({ref['url']})**: {ref['content']}...")
    else:
        st.write("No references found.")
