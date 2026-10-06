import streamlit as st
import os
from dotenv import load_dotenv
from pypdf import PdfReader
from groq import Groq

load_dotenv()

st.title("LLM-Crash Detector - Hallucination Guard")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY nahi mila. .env file check karo.")
    st.stop()

client = Groq(api_key=api_key)

pdf = st.file_uploader("PDF daalo", type="pdf")

if pdf:
    reader = PdfReader(pdf)

    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    text = text[:7000]

    st.success("PDF Ready")

    q = st.text_input("Sawal:")

    if q:
        prompt = f"""
You are a strict PDF question-answering system.

PDF CONTENT:
{text}

USER QUESTION:
{q}

STRICT RULES:
1. Answer ONLY using information explicitly present in the PDF.
2. Do NOT use your own knowledge.
3. Do NOT guess or infer missing information.
4. Do NOT assume that something is true just because it is likely.
5. If the exact answer cannot be found in the PDF, respond EXACTLY with:
Iska jawab PDF me nahi hai
6. For questions about skills, companies, salary, blood group,
   education, experience, location, or any other personal information,
   the information MUST explicitly appear in the PDF.
7. If even one important part of the question is not supported by
   the PDF, respond:
Iska jawab PDF me nahi hai

Now answer the user's question.
"""

        try:
            resp = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a strict hallucination guard. "
                            "Never provide information that is not explicitly "
                            "supported by the supplied PDF."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )

            answer = resp.choices[0].message.content.strip()

            st.write(answer)

        except Exception as e:
            st.error(f"Groq Error: {e}")
