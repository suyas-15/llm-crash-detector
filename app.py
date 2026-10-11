import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader

load_dotenv(override=True)

def get_crash_score(prompt):
    score = 0
    risky_words = ["ignore","delete","format","system","hack","bypass","override","jailbreak","previous instructions", "disregard", "forget"]
    for word in risky_words:
        if word in prompt.lower():
            score += 35
    return min(score, 100)

def get_score_color(score):
    if score < 30:
        return "green"
    elif score < 60:
        return "orange"
    else:
        return "red"

st.set_page_config(page_title="LLM-Crash Detector", page_icon="🛡", layout="wide")
st.title("LLM-Crash Detector - Day 6 Admin Dashboard")

api_key = os.getenv("GROQ_API_KEY")
if api_key:
    api_key = api_key.strip().strip('"').strip("'")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "blocked_logs" not in st.session_state:
    st.session_state.blocked_logs = []

with st.sidebar:
    st.metric("Total chats", len(st.session_state.messages))
    st.metric("Blocked Prompts", len(st.session_state.blocked_logs))
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    if st.session_state.blocked_logs:
        st.subheader("🚨 Blocked Logs")
        st.dataframe(st.session_state.blocked_logs, use_container_width=True)
        if st.button("Clear Logs", use_container_width=True):
            st.session_state.blocked_logs = []
            st.rerun()
    st.divider()
    st.caption("Day 6 - Admin Dashboard")

uploaded_file = st.file_uploader("PDF Upload Karo", type="pdf")
if uploaded_file:
    reader = PdfReader(uploaded_file)
    pdf_text = ""
    for page in reader.pages:
        pdf_text += page.extract_text() or ""
    st.session_state.pdf_text = pdf_text
    st.success(f"PDF Read! {len(pdf_text)} chars")
else:
    if not st.session_state.pdf_text:
        st.info("Pehle PDF upload karo")

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
        st.progress(score/100, text=f"Crash Score: {score}%")
        st.markdown(f":{color}[Crash Score: {score}%]")

    if score >= 60:
        st.session_state.blocked_logs.append({"prompt": query, "score": score})
        reply = "🚨 Risky prompt block kiya! Ye prompt unsafe hai, isliye LLM ko nahi bheja."
    else:
        if not st.session_state.pdf_text:
            reply = "Pehle PDF upload karo fir sawal pucho!"
        else:
            try:
                client = Groq(api_key=api_key)
                res = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role":"user","content":f"Resume:{st.session_state.pdf_text[:15000]} Q:{query}"}],
                    temperature=0
                )
                reply = res.choices[0].message.content
            except Exception as e:
                reply = f"Groq Error: {e}"

    with st.chat_message("assistant"):
        st.write(reply)
    st.session_state.messages.append({"role":"assistant","content":reply})