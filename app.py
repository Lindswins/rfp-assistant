
import streamlit as st
import openai
import PyPDF2
import docx2txt
from io import StringIO

st.set_page_config(page_title="RFP Assistant", layout="centered")

st.title("📄 AI-Powered RFP Assistant")
st.write("Upload your past RFPs and ask a question. Get a draft response based on your history.")

# Input OpenAI API key
api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")
if api_key:
    openai.api_key = api_key

    uploaded_files = st.file_uploader("📁 Upload past RFP documents", type=["pdf", "docx", "txt"], accept_multiple_files=True)

    question = st.text_area("💬 Enter a new RFP question you'd like help answering:")

    if st.button("✨ Generate Answer"):
        all_text = ""

        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith(".pdf"):
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    all_text += page.extract_text()
            elif uploaded_file.name.endswith(".docx"):
                all_text += docx2txt.process(uploaded_file)
            elif uploaded_file.name.endswith(".txt"):
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                all_text += stringio.read()

        if not all_text.strip():
            st.warning("No text extracted from uploaded documents.")
        else:
            with st.spinner("Generating..."):
                prompt = f"""Based on the following past RFP content, generate a high-quality answer to this question:

Question: {question}

Relevant Past Content:
{all_text}
"""
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.4,
                        max_tokens=600
                    )
                    answer = response['choices'][0]['message']['content']
                    st.success("✅ Suggested Answer:")
                    st.text_area("Answer", answer, height=200)
                except Exception as e:
                    st.error(f"Error from OpenAI: {e}")
