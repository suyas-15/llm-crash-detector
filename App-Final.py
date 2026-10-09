import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
from datetime import datetime

load_dotenv(override=True)

def get_crash_score(prompt):
    score = 0
    risky_words = ["ignore","delete","format","system","hack","bypass","override","jailbreak"]
    for word in risky_words:
        if word in prompt.lower():
            score += 20
    return min(score, 100)

def get_score_color(score):
    if score < 30:
        return "green"
    elif score < 60:
        return "orange"
    else:
        return "red"

st.set_page_config(page_title="LLM-Crash Detector", page_icon="🛡️", layout="wide")
st.title("LLM-Crash Detector - Day 4")
st.write("Chat History + Color Crash Score + Clear Chat")

# --- API Key - Local First (No Warning) ---
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = None

if api_key:
    api_key = api_key.strip().strip('"').strip("'")

# --- Session State for History ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    if st.session_state.pdf_name:
        st.info(f"📄 Loaded: {st.session_state.pdf_name}")
        st.caption(f"{len(st.session_state.pdf_text)} chars")
    st.caption(f"Total chats: {len(st.session_state.messages)}")

uploaded_file = st.file_uploader("PDF Upload Karo", type="pdf")

if uploaded_file:
    if uploaded_file.name != st.session_state.pdf_name:
        reader = PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() or ""
        st.session_state.pdf_text = pdf_text
        st.session_state.pdf_name = uploaded_file.name
        st.session_state.messages = [] # new PDF = new chat
    
    st.success(f"PDF Read Ho Gaya! {len(st.session_state.pdf_text)} characters")

    # --- Show Chat History ---
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "score" in msg:
                color = get_score_color(msg["score"])
                st.markdown(f":{color}[Crash Score: {msg['score']}%]")
            if "time" in msg:
                st.caption(msg["time"])

    # --- New Input ---
    query = st.chat_input("Sawal pucho...")

    if query:
        score = get_crash_score(query)
        color = get_score_color(score)
        time_now = datetime.now().strftime("%I:%M %p")

        # User message add
        st.session_state.messages.append({"role": "user", "content": query, "time": time_now, "score": score})
        with st.chat_message("user"):
            st.markdown(query)
            st.markdown(f":{color}[Crash Score: {score}%] - {time_now}")

        # Bot logic
        if score >= 60:
            bot_reply = "🚨 Ye prompt risky hai! LLM crash ho sakta hai. Isliye block kiya."
            with st.chat_message("assistant"):
                st.error(bot_reply)
        else:
            if not api_key:
                bot_reply = "GROQ_API_KEY nahi mili!"
            elif not api_key.startswith("gsk_"):
                bot_reply = f"Invalid API Key format! Must start with gsk_"
            else:
                try:
                    client = Groq(api_key=api_key)
                    prompt = f"""
                    Tumhe ek Resume diya gaya hai. Sirf isi resume se jawab do.
                    Agar jawab resume me nahi hai toh EXACT bolna: "Iska jawab PDF me nahi hai"
                    
                    RESUME TEXT:
                    {st.session_state.pdf_text[:15000]}
                    
                    SAWAL:
                    {query}
                    """
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0,
                    )
                    bot_reply = response.choices[0].message.content
                except Exception as e:
                    bot_reply = f"Groq API Error: {e}"

            with st.chat_message("assistant"):
                st.markdown(bot_reply)
                st.caption(time_now)

        # Save bot message
        st.session_state.messages.append({"role": "assistant", "content": bot_reply, "time": time_now, "score": score})

else:
    if st.session_state.pdf_text:
        # PDF already in session
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "score" in msg:
                    color = get_score_color(msg["score"])
                    st.markdown(f":{color}[Crash Score: {msg['score']}%]")
        query = st.chat_input("Sawal pucho...")
        if query:
            st.rerun()
    else:
        st.info("Pehle PDF upload karo")
