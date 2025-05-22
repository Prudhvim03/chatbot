import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage
import requests

# --- Load environment variables ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

AGENT_NAME = "Terrคi"
AGENT_INTRO = (
    f"Hi, I am {AGENT_NAME}, your AI-powered farming assistant! "
    "I am created by Prudhvi, a broader-ideology person introducing PrudhΛi: "
    "a vision of advanced technology, research, and development for the future of agriculture. "
    "My mission is to empower Indian farmers and agri-students with practical, region-specific, and AI-driven guidance."
)

# --- Set up LLM and Tavily Search ---
llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)
tavily_search = TavilySearch(api_key=TAVILY_API_KEY, max_results=3)

# --- Weather API ---
def get_weather(location):
    if not location:
        return "Please provide a location for weather information."
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
    resp = requests.get(url).json()
    if resp.get("main"):
        temp = resp["main"]["temp"]
        weather = resp["weather"][0]["description"].capitalize()
        return f"🌦️ Weather in {location}: {weather}, {temp}°C"
    else:
        return "Weather data not available for this location."

def get_weather_details(location):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
    resp = requests.get(url).json()
    if resp.get("main"):
        humidity = resp["main"].get("humidity", "N/A")
        wind = resp["wind"].get("speed", "N/A")
        desc = resp["weather"][0]["description"].capitalize()
        temp = resp["main"]["temp"]
        feels = resp["main"].get("feels_like", "N/A")
        more = (
            f"🌡️ Detailed weather for {location}:\n"
            f"- Description: {desc}\n"
            f"- Temperature: {temp}°C (feels like {feels}°C)\n"
            f"- Humidity: {humidity}%\n"
            f"- Wind speed: {wind} m/s"
        )
        return more
    else:
        return "Sorry, I couldn't fetch more details for this location."

# --- Helper functions ---
def is_greeting(msg):
    return msg.strip().lower() in ["hi", "hello", "hey"]

def is_more_explanation(msg):
    return any(word in msg.lower() for word in ["more", "explain", "details", "explanation", "expand", "root", "step", "why", "how"])

def extract_location_from_query(msg):
    msg = msg.lower()
    if "weather in " in msg:
        return msg.split("weather in ")[-1].strip().capitalize()
    if "in " in msg:
        return msg.split("in ")[-1].strip().capitalize()
    return ""

def is_weather_query(msg):
    return "weather" in msg.lower()

def short_llm_answer(question):
    # Weather queries handled separately
    if is_weather_query(question):
        location = extract_location_from_query(question)
        return get_weather(location)
    # Use Tavily for a quick fact/summary
    tavily_result = tavily_search.invoke({"query": question})
    summary = tavily_result.get("results", [{}])[0].get("content", "")
    if summary:
        return summary.strip().split("\n")[0][:500]  # First sentence, max 180 chars
    # Fallback to LLM
    system_prompt = "Answer the following farming question in one short, root-level sentence for a busy Indian farmer."
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ]
    response = llm.invoke(messages)
    return response.content.strip().split("\n")[0][:500]

def detailed_llm_answer(question, user_name):
    # Weather queries handled separately
    if is_weather_query(question):
        location = extract_location_from_query(question)
        return get_weather_details(location)
    # Use both Tavily and LLM for a detailed explanation
    tavily_result = tavily_search.invoke({"query": question})
    web_context = ""
    if tavily_result.get("results"):
        web_context = "\n".join([r.get("content", "") for r in tavily_result["results"]])
    system_prompt = (
        f"You are Terrคi, an Indian agricultural AI assistant created by Prudhvi (PrudhΛi), "
        f"focused on research, technology, and practical solutions. "
        f"Give a detailed, region-specific, step-by-step answer for {user_name}. "
        "Always explain in clear, simple language. Mention local varieties, climate, and sustainable practices where relevant."
    )
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question + "\n\n" + web_context)
    ]
    response = llm.invoke(messages)
    return response.content.strip()

# --- Conversation State ---
if "step" not in st.session_state:
    st.session_state.step = "greet"
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "last_short_answer" not in st.session_state:
    st.session_state.last_short_answer = ""
if "last_query_type" not in st.session_state:
    st.session_state.last_query_type = ""
if "last_question" not in st.session_state:
    st.session_state.last_question = ""
if "last_location" not in st.session_state:
    st.session_state.last_location = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UI ---
st.title("Terrคi: Your AI Farming Assistant")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Type your message...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Step 1: Greeting
    if st.session_state.step == "greet":
        if is_greeting(prompt):
            response = f"{AGENT_INTRO}\n\nWhat is your name?"
            st.session_state.step = "ask_name"
        else:
            response = f"Please say 'Hi' or 'Hello' to start."
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Step 2: Get User Name
    elif st.session_state.step == "ask_name":
        user_name = prompt.strip().split()[0].capitalize()
        st.session_state.user_name = user_name
        response = (
            f"I am happy to assist you in farming related queries, {user_name}. "
            "Please ask your question."
        )
        st.session_state.step = "main"
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Step 3: Main Q&A
    elif st.session_state.step == "main":
        # More Explanation Request
        if is_more_explanation(prompt):
            if st.session_state.last_query_type in ["llm", "weather"]:
                question = st.session_state.last_question
                more = detailed_llm_answer(question, st.session_state.user_name)
                with st.chat_message("assistant"):
                    st.markdown(more)
                st.session_state.messages.append({"role": "assistant", "content": more})
            else:
                more = "Please ask a farming question first, then request more explanation."
                with st.chat_message("assistant"):
                    st.markdown(more)
                st.session_state.messages.append({"role": "assistant", "content": more})

        # Any other query (short answer only)
        else:
            # Use Groq+Tavily for short, root-level answer or weather
            short_answer = short_llm_answer(prompt)
            st.session_state.last_short_answer = short_answer
            st.session_state.last_query_type = "weather" if is_weather_query(prompt) else "llm"
            st.session_state.last_question = prompt
            with st.chat_message("assistant"):
                st.markdown(short_answer)
            st.session_state.messages.append({"role": "assistant", "content": short_answer})

# --- Footer ---
st.markdown(
    "<div style='text-align:center; color:#8d6e63; margin-top:2rem;'>"
    "Developed by Prudhvi (PrudhΛi) • May 2025"
    "</div>",
    unsafe_allow_html=True
)
