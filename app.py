import streamlit as st
import os
from dotenv import load_dotenv
from pypdf import PdfReader
from groq import Groq

load_dotenv()

st.set_page_config(page_title="LLM-Crash Detector")
st.title("LLM-Crash Detector - Day 2 Final")
st.write("Complete Hallucination Guard")

uploaded_file = st.file_uploader("PDF Upload Karo", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    pdf_text = ""
    for page in reader.pages:
        pdf_text += page.extract_text() or ""

    st.success(f"PDF Read Ho Gaya! {len(pdf_text)} characters")

    query = st.text_input("Sawal pucho")

    if query:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = f"""
        Tumhe ek Resume diya gaya hai. Sirf isi resume se jawab do.
        Agar jawab resume me nahi hai toh EXACT bolna: "Iska jawab PDF me nahi hai"
        Jhootha jawab kabhi mat dena. Hallucinate mat karo.

        Instructions:
        1. Context se bahar ka jawab mat do
        2. Agar info nahi hai toh mana kar do
        3. Confidence ke saath jhooth mat bolo

        RESUME TEXT:
        {pdf_text[:15000]}

        SAWAL: {query}
        JAWAB:
        """

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        st.write("### Jawab:")
        st.write(response.choices[0].message.content)
else:
    st.info("Pehle PDF upload karo")