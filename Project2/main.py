import streamlit as st
import PyPDF2
import io
import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Page Configuration
st.set_page_config(page_title="Resume Critiquer", page_icon="📃", layout="centered")
st.title("Resume Critiquer 📃")
st.markdown("Upload your resume and get feedback on how to improve it!")

# 3. API Key Setup
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Google API Key not found. Please check your .env file and ensure the variable is GOOGLE_API_KEY.")
    st.stop()

# Configure the Gemini Library
genai.configure(api_key=GOOGLE_API_KEY,transport='rest')

# 4. Helper Functions
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

# 5. UI Elements
uploaded_file = st.file_uploader("Choose a PDF or Text file", type=["pdf", "text"])
job_role = st.text_input("Enter the job role you are applying for:")
analyze_button = st.button("Analyze Resume")

# 6. Main Logic
# 6. Main Logic
if analyze_button and uploaded_file:
    try:
        # Extract content
        file_content = extract_text_from_file(uploaded_file)
        
        if not file_content.strip():
            st.error("The uploaded file is empty.")
            st.stop()

        # Initialize the model - Updated to the 2026 stable version
        MODEL_NAME = "gemini-2.5-flash"  # Updated to the latest stable version
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Construct the Prompt (Fixed the quote marks)
        prompt = f"""
        You are an expert resume reviewer with years of experience in HR and recruitment. 
        Please critique the following resume and provide suggestions for improvement. 
        
        Target Job Role: {job_role if job_role else 'General Application'}

        Resume Content:
        {file_content}

        Focus on:
        1. Content clarity and impact (use of action verbs and metrics).
        2. Skills presentation.
        3. Experience descriptions.
        4. Specific improvements for the {job_role} role.
        
        Please provide your analysis in a clear, structured format with specific recommendations.
        """

        # Generate Response
        with st.spinner("Gemini is analyzing your resume..."):
            response = model.generate_content(prompt)
        
        # Display Results
        st.markdown("---")
        st.markdown("### Analysis Results")
        st.markdown(response.text)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        
