import os
import streamlit as st
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage

# --- Load environment variables ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY")

# --- Set up LLM and Tavily Search ---
llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)
tavily_search = TavilySearch(api_key=TAVILY_API_KEY, max_results=3)

# --- Weather API Function ---
def get_weather(location, api_key):
    if not location:
        return ""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    resp = requests.get(url).json()
    if resp.get("main"):
        temp = resp["main"]["temp"]
        weather = resp["weather"][0]["description"].capitalize()
        return f"**🌦️ Weather in {location}:** {weather}, {temp}°C"
    else:
        return "Weather data not available for this location."

# --- Google Translate API Function ---
def translate(text, target_lang):
    if target_lang == "en":
        return text
    url = f"https://translation.googleapis.com/language/translate/v2"
    params = {
        "q": text,
        "target": target_lang,
        "key": GOOGLE_TRANSLATE_API_KEY
    }
    resp = requests.post(url, data=params).json()
    try:
        return resp["data"]["translations"][0]["translatedText"]
    except Exception:
        return text

# --- Greeting and Farewell Functions ---
def greet_user(lang="en"):
    greetings = {
        "en": "👋 Namaste! Welcome to your smart farming assistant.",
        "hi": "👋 नमस्ते! आपके स्मार्ट कृषि सहायक में स्वागत है।",
        "te": "👋 నమస్తే! మీ స్మార్ట్ వ్యవసాయ సహాయకుడికి స్వాగతం.",
        "ta": "👋 வணக்கம்! உங்கள் ஸ்மார்ட் விவசாய உதவியாளருக்கு வரவேற்கின்றேன்.",
    }
    return greetings.get(lang, greetings["en"])

def farewell_user(lang="en", summary=""):
    farewells = {
        "en": f"Thank you for using our service. Here’s a brief of our conversation: {summary}\nI am happy to see you again! ❤️",
        "hi": f"हमारी सेवा का उपयोग करने के लिए धन्यवाद। हमारी बातचीत का सारांश: {summary}\nफिर से आपकी सेवा में उपस्थित होकर खुशी हुई! ❤️",
        "te": f"మా సేవను ఉపయోగించినందుకు ధన్యవాదాలు. మా సంభాషణ సారాంశం: {summary}\nమిమ్మల్ని మళ్లీ చూసినందుకు ఆనందంగా ఉంది! ❤️",
        "ta": f"எங்கள் சேவையை பயன்படுத்தியதற்கு நன்றி. நமது உரையாடல் சுருக்கம்: {summary}\nஉங்களை மீண்டும் சந்திப்பதில் மகிழ்ச்சி! ❤️",
    }
    return farewells.get(lang, farewells["en"])

# --- Summarize Conversation ---
def summarize_conversation(messages):
    # Summarize last 3 user/assistant messages
    summary = []
    for m in messages[-6:]:
        if m["role"] == "user":
            summary.append(f"User: {m['content']}")
        else:
            summary.append(f"AI: {m['content'][:60]}...")
    return " | ".join(summary)

# --- Farming Solution (Root-level, Location-based) ---
def farming_solution(location, crop, issue, lang="en"):
    prompt = (
        f"You are an Indian agricultural expert. Give step-by-step, practical, region-specific advice for the following:\n"
        f"Location: {location}\nCrop: {crop}\nIssue: {issue}\n"
        f"Include local varieties, soil, weather, sustainable practices. Keep it simple and actionable."
    )
    messages = [
        SystemMessage(content="You are a helpful Indian farming assistant."),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages)
    return response.content.strip()

# --- Custom Agent (You can extend this) ---
def my_agent(question, location=None, lang="en"):
    # Basic logic: try to extract crop/location/issue, else fallback to LLM
    crop, issue = "", ""
    # Simple extraction (can be improved)
    if "for" in question:
        parts = question.split("for")
        issue = parts[0].strip()
        rest = parts[1].strip()
        if "," in rest:
            crop, location = rest.split(",", 1)
            crop = crop.strip()
            location = location.strip()
        else:
            crop = rest.strip()
    # If location or crop missing, ask user
    if not location:
        location = "India"
    if not crop:
        crop = "general crops"
    if not issue:
        issue = question
    # Get weather
    weather_info = get_weather(location, OPENWEATHER_API_KEY)
    # Get farming solution
    solution = farming_solution(location, crop, issue, lang)
    return f"{weather_info}\n\n{solution}"

# --- Streamlit UI ---
st.set_page_config(page_title="Terrคi: The Futuristic AI Farming Guide", page_icon="🌾", layout="centered")

# --- Colorful Header (SVG, CSS) ---
futuristic_logo_svg = """<svg width="72" height="72" ...> ... </svg>"""  # (use your SVG from previous code)
st.markdown(f'<div class="futuristic-logo">{futuristic_logo_svg}</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🌾 Terrคi: The Futuristic AI Farming Guide</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Empowering Indian farmers with AI, real-time insights, and smart agriculture innovations</div>', unsafe_allow_html=True)

# --- Language Selector ---
lang_map = {"English": "en", "Hindi": "hi", "Telugu": "te", "Tamil": "ta"}
user_lang_name = st.selectbox("Choose your language:", list(lang_map.keys()), index=0)
user_lang = lang_map[user_lang_name]

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ended" not in st.session_state:
    st.session_state.ended = False

# --- Show Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Greeting on first load ---
if not st.session_state.messages:
    greeting = greet_user(user_lang)
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    with st.chat_message("assistant"):
        st.markdown(greeting)

# --- Chat Input ---
if not st.session_state.ended:
    prompt = st.chat_input("Ask about farming, soil, pests, irrigation, weather, or anything in agriculture…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Consulting AI experts and real-time data..."):
                # Custom agent logic
                agent_response = my_agent(prompt, lang=user_lang)
                # Translate if needed
                final_response = translate(agent_response, user_lang)
                st.markdown(final_response)
                st.session_state.messages.append({"role": "assistant", "content": final_response})
        # Ask if user wants to end
        if st.button("End Conversation"):
            st.session_state.ended = True

# --- Conversation End ---
if st.session_state.ended:
    summary = summarize_conversation(st.session_state.messages)
    farewell = farewell_user(user_lang, summary)
    with st.chat_message("assistant"):
        st.markdown(farewell)

# --- Footer ---
st.markdown(
    "<div style='text-align:center; color:#8d6e63; margin-top:2rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi • May 2025"
    "</div>",
    unsafe_allow_html=True
)
