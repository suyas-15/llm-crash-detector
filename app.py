import streamlit as st
import os
from pypdf import PdfReader
from groq import Groq

st.set_page_config(page_title="LLM-Crash Detector")

st.title("LLM-Crash Detector - Hallucination Guard")

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("GROQ_API_KEY nahi mila..env file check karo.")
    st.stop()

client = Groq(api_key=api_key)

pdf = st.file_uploader("PDF daalo", type="pdf")

if pdf:
    reader = PdfReader(pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    text = text[:15000]
    st.success(f"PDF Ready - {len(text)} chars loaded")

    q = st.text_input("Sawal:")

    if q and st.button("Pucho"):
        prompt = f"""
You are a strict PDF question-answering system.
PDF CONTENT:
{text}
USER QUESTION:
{q}
RULE: Answer ONLY from PDF, else reply EXACTLY: Iska jawab PDF me nahi hai
"""

        try:
            resp = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": "You are a strict hallucination guard."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            answer = resp.choices[0].message.content.strip()

            st.write("### Answer:")
            st.write(answer)
            st.divider()

            if "pdf me nahi hai" in answer.lower():
                st.success("✅ SAFE - No Hallucination")
            else:
                st.info("⚠️ Answer PDF se diya hai - Manual verify kar lo")

        except Exception as e:
            st.error(f"Groq Error: {e}")
