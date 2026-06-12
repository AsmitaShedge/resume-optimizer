import spacy
import re

nlp = spacy.load("en_core_web_sm")

# Define strong action verbs
STRONG_VERBS = {
    "developed", "led", "implemented", "created",
    "designed", "achieved", "improved", "increased"
}

# Define must-have keywords for a tech resume
REQUIRED_KEYWORDS = {
    "python", "machine learning", "data analysis",
    "sql", "project", "team"
}

def analyze_resume(text, resume_id=None):
    suggestions = []
    score = 100
    ats_score = 100

    doc = nlp(text.lower())

    # Suggestion 1: Check for missing keywords
    missing_keywords = [kw for kw in REQUIRED_KEYWORDS if kw not in text.lower()]

    if missing_keywords:
        suggestions.append(
            f"Consider adding important keywords: {', '.join(missing_keywords)}"
        )
        score -= len(missing_keywords) * 5
        ats_score -= len(missing_keywords) * 5

    # Suggestion 2: Check if strong action verbs are used
    verbs = {token.lemma_ for token in doc if token.pos_ == "VERB"}

    if not STRONG_VERBS.intersection(verbs):
        suggestions.append(
            "Consider using strong action verbs like 'developed', 'implemented', or 'led'."
        )
        score -= 15
        ats_score -= 10

    # Suggestion 3: Resume too short
    word_count = len([token.text for token in doc if not token.is_punct])

    if word_count < 100:
        suggestions.append(
            "Your resume seems too short. Add more details about your experience."
        )
        score -= 10
        ats_score -= 10

    # Suggestion 4: Contact Info
    if not re.search(r'\b\d{10}\b', text) and not re.search(r'\+91[-\s]?\d{10}', text):
        suggestions.append("Include a valid phone number.")
        score -= 10

    if not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text):
        suggestions.append("Include a professional email address.")
        score -= 10

    score = max(score, 0)
    ats_score = max(ats_score, 0)

    return score, ats_score, suggestions