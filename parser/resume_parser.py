import re
import fitz  # PyMuPDF
import docx
import os
import spacy
import re

SKILLS = [
    "python",
    "sql",
    "machine learning",
    "data analysis",
    "java",
    "c++",
    "html",
    "css",
    "javascript",
    "excel",
    "power bi",
    "tableau",
    "deep learning",
    "numpy",
    "pandas"
]

nlp = spacy.load("en_core_web_sm")

def parse_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def parse_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def parse_resume(file_path):

    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".pdf":
        text = parse_pdf(file_path)

    elif ext == ".docx":
        text = parse_docx(file_path)

    else:
        raise ValueError("Unsupported file format")

    doc = nlp(text)

    name = None
    email = None
    phone = None
    
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    if lines:
        name = lines[0]

    email_match = re.search(r'\S+@\S+\.\S+', text)
    if email_match:
        email = email_match.group()

    phone_match = re.search(
        r'(\+?\d{1,4}[-.\s]?)?(\(?\d{3,5}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{4}',
        text
    )

    if phone_match:
        phone = phone_match.group()

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "resume_text": text
    }

def extract_skills(text):
    text = text.lower()

    found_skills = []

    for skill in SKILLS:
        if skill in text:
            found_skills.append(skill)

    return found_skills

def extract_experience(text):
    pattern = r'(\d+)\+?\s*(?:years?|yrs?)'

    match = re.search(
        pattern,
        text.lower()
    )

    if match:
        return match.group(1) + " Years"

    return "Fresher"