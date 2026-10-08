import streamlit as st
import os
from dotenv import load_dotenv
from pypdf import PdfReader
from groq import Groq

load_dotenv()

def get_crash_score(prompt):
    score = 0
    risky_words = ["ignore", "delete", "format", "system", "hack", "bypass", "override", "jailbreak"]
    for word in risky_words:
        if word in prompt.lower():
            score += 20
    return min(score, 100)

st.set_page_config(page_title="LLM-Crash Detector")
st.title("LLM-Crash Detector - Day 3")
st.write("Complete Hallucination Guard + Crash Score")

uploaded_file = st.file_uploader("PDF Upload Karo", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    pdf_text = ""
    for page in reader.pages:
        pdf_text += page.extract_text() or ""
    st.success(f"PDF Read Ho Gaya! {len(pdf_text)} characters")

    query = st.text_input("Sawal pucho")

    if query:
        score = get_crash_score(query)
        st.warning(f"⚠ Crash Score: {score}%")

        if score >= 60:
            st.error("Ye prompt risky hai! LLM crash ho sakta hai.")
        else:
            api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
            client = Groq(api_key=api_key)
            prompt = f"""
            Tumhe ek Resume diya gaya hai. Sirf isi resume se jawab do.
            Agar jawab resume me nahi hai toh EXACT bolna: "Iska jawab PDF me nahi hai"
            RESUME TEXT: {pdf_text[:15000]}
            SAWAL: {query}
            """
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            st.write("### Jawab:")
            st.write(response.choices[0].message.content)
else:
    st.info("Pehle PDF upload karo")