import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader

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

st.set_page_config(page_title="LLM-Crash Detector", page_icon="🛡", layout="wide")
st.title("LLM-Crash Detector - Day 4")

# ONLY.env se lega, secrets check hi nahi karega
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    api_key = api_key.strip().strip('"').strip("'")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

with st.sidebar:
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.write(f"Total chats: {len(st.session_state.messages)}")

uploaded_file = st.file_uploader("PDF Upload Karo", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    pdf_text = ""
    for page in reader.pages:
        pdf_text += page.extract_text() or ""
    st.session_state.pdf_text = pdf_text
    st.success(f"PDF Read! {len(pdf_text)} chars")

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    query = st.chat_input("Sawal pucho")
    if query:
        score = get_crash_score(query)
        color = get_score_color(score)
        st.session_state.messages.append({"role":"user","content":query})
        with st.chat_message("user"):
            st.write(query)
            st.markdown(f":{color}[Crash Score: {score}%]")

        if score >= 60:
            reply = "🚨 Risky prompt block kiya!"
        else:
            client = Groq(api_key=api_key)
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":f"Resume:{pdf_text[:15000]} Q:{query}"}], temperature=0)
            reply = res.choices[0].message.content

        with st.chat_message("assistant"):
            st.write(reply)
        st.session_state.messages.append({"role":"assistant","content":reply})
else:
    st.info("Pehle PDF upload karo")