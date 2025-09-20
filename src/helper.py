import fitz # PyMuPDF
import os 
from dotenv import load_dotenv
from groq import Groq
import streamlit as st


load_dotenv()

# Try Streamlit secrets first, fallback to environment variables
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)


def extract_text_from_pdf(uploaded_file):
    """
    Extracts text from a PDF file.
    
    Args:
        uploaded_file (str): The path to the PDF file.
        
    Returns:
        str: The extracted text.
    """
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text



def ask_openai(prompt, max_tokens=500):
    """
    Sends a prompt to the Groq API and returns the response.
    
    Args:
        prompt (str): The prompt to send to the Groq API.
        max_tokens (int): The maximum tokens for the response.
        
    Returns:
        str: The response from the Groq API.
    """
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.5,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content


def validate_resume(text):
    """
    Validates if the extracted text appears to be from a resume.
    
    Args:
        text (str): The extracted text from the PDF.
        
    Returns:
        bool: True if it appears to be a resume, False otherwise.
    """
    if not text or len(text.strip()) < 100:
        return False
    
    text_lower = text.lower()
    
    # Check for common resume keywords
    resume_keywords = [
        'experience', 'education', 'skills', 'work', 'employment',
        'qualification', 'degree', 'university', 'college', 'job',
        'position', 'role', 'responsibility', 'achievement', 'project',
        'email', 'phone', 'contact', 'address', 'linkedin', 'github'
    ]
    
    keyword_count = sum(1 for keyword in resume_keywords if keyword in text_lower)
    
    # Must have at least 3 resume-related keywords
    return keyword_count >= 3


