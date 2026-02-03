import streamlit as st
from pypdf import PdfReader
from openai import OpenAI

st.set_page_config(page_title="PDF Lecture Bot", page_icon="📚")
st.title("📚 PDF Lecture Bot")
st.write("Upload a text PDF and get a lecture-style explanation.")

# OpenAI client reads key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

uploaded = st.file_uploader("Upload your PDF", type=["pdf"])

level = st.selectbox("Level", ["Beginner", "University", "Advanced"])
minutes = st.slider("Lecture length (minutes)", 5, 45, 15)

if uploaded:
    reader = PdfReader(uploaded)
    text = ""
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        text += f"\n\n[Page {i+1}]\n{page_text}"

    st.subheader("PDF preview")
    st.code(text[:1200])

    if st.button("🎤 Generate lecture"):
        level_rules = {
            "Beginner": "Use very simple language, define terms, and give everyday analogies.",
            "University": "Teach like a university lecturer: intuition first, structured explanation, then examples.",
            "Advanced": "Assume strong background. Be precise and technical, but still explain clearly."
        }

        prompt = f"""
You are a university lecturer.
Turn the PDF content into a lecture.

Rules:
- Stick to the PDF content only. If something isn't in the PDF, say so.
- Use headings and a clear structure.
- Add 2-3 examples.
- End with:
  1) recap bullets
  2) 8 quiz questions with short answers
- Target about {minutes} minutes of lecture length.
- Level: {level_rules[level]}

PDF CONTENT:
{text}
"""

        with st.spinner("Generating..."):
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful university lecturer."},
                    {"role": "user", "content": prompt},
                ],
            )

        st.subheader("Lecture")
        st.write(resp.choices[0].message.content)
