import google.generativeai as genai
from dotenv import load_dotenv
import os
import PyPDF2
load_dotenv()

def extract_text_from_pdf(pdf_path):
    with open('sq.pdf', 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        # Read each page and extract text
        for page in reader.pages:
            text = page.extract_text()
            print(text)


def main():
    genai.configure(api_key=os.environ["API_KEY"])

    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    response = model.generate_content("What is the meaning of life?",stream=True)


