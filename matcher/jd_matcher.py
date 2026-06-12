from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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


def extract_skills_from_text(text):
    text = text.lower()

    found_skills = []

    for skill in SKILLS:
        if skill in text:
            found_skills.append(skill)

    return found_skills


def calculate_match_score(resume_text, jd_text):

    documents = [resume_text, jd_text]

    cv = CountVectorizer()

    matrix = cv.fit_transform(documents)

    similarity = cosine_similarity(matrix)[0][1]

    return round(similarity * 100, 2)


def calculate_ats_score(resume_text, jd_text):

    resume_skills = extract_skills_from_text(
        resume_text
    )

    jd_skills = extract_skills_from_text(
        jd_text
    )

    matched_skills = []

    missing_skills = []

    for skill in jd_skills:

        if skill in resume_skills:
            matched_skills.append(skill)

        else:
            missing_skills.append(skill)

    if len(jd_skills) > 0:

        ats_score = round(
            (len(matched_skills) / len(jd_skills)) * 100,
            2
        )

    else:
        ats_score = 0

    return (
        ats_score,
        matched_skills,
        missing_skills
    )