import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader

load_dotenv(override=True)


def get_crash_score(prompt):
    score = 0
    risky_words = [
        "ignore",
        "delete",
        "format",
        "system",
        "hack",
        "bypass",
        "override",
        "jailbreak",
    ]
    for word in risky_words:
        if word in prompt.lower():
            score += 20
    return min(score, 100)


st.set_page_config(page_title="LLM-Crash Detector", page_icon="🛡")
st.title("LLM-Crash Detector - Day 3")
st.write("Complete Hallucination Guard + Crash Score")

# Robust API Key Retrieval
api_key = None

# Priority 1: Streamlit Cloud Secrets
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
# Priority 2: Local .env File
elif os.getenv("GROQ_API_KEY"):
    api_key = os.getenv("GROQ_API_KEY")

# Clean formatting (spaces/quotes remove karne ke liye)
if api_key:
    api_key = api_key.strip().strip('"').strip("'")

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
            if not api_key:
                st.error(
                    "GROQ_API_KEY nahi mili! Streamlit Secrets ya .env file check karein."
                )
            elif not api_key.startswith("gsk_"):
                st.error(
                    f"Invalid API Key format! Key starting with '{api_key[:4]}' is invalid. Must start with 'gsk_'."
                )
            else:
                try:
                    client = Groq(api_key=api_key)
                    prompt = f"""
                    Tumhe ek Resume diya gaya hai. Sirf isi resume se jawab do.
                    Agar jawab resume me nahi hai toh EXACT bolna: "Iska jawab PDF me nahi hai"
                    
                    RESUME TEXT:
                    {pdf_text[:15000]}
                    
                    SAWAL:
                    {query}
                    """
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0,
                    )
                    st.write("### Jawab:")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Groq API Error: {e}")
else:
    st.info("Pehle PDF upload karo")