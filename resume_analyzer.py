import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Support both PyPDF2 and pypdf imports seamlessly
try:
    import PyPDF2
    PdfReader = PyPDF2.PdfReader
except ImportError:
    try:
        import pypdf
        PdfReader = pypdf.PdfReader
    except ImportError:
        PdfReader = None

# Try loading spaCy, fallback to regex-based processing if model isn't pre-loaded
try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        nlp = None
except ImportError:
    nlp = None

# Curated list of Python & Modern Tech Ecosystem skills (single & multi-word)
KNOWN_SKILLS = [
    # Core Languages & Runtimes
    "python", "javascript", "typescript", "html", "css", "sql", "r", "bash", "shell", "java",
    # Frameworks & Libraries
    "flask", "django", "fastapi", "react", "vue", "angular", "bootstrap", "tailwind",
    "jinja", "express", "node.js", "nodejs", "jquery",
    # Data Science, AI & ML
    "pandas", "numpy", "scipy", "scikit-learn", "sklearn", "tensorflow", "keras", "pytorch",
    "matplotlib", "seaborn", "nlp", "spacy", "nltk", "opencv", "data science", "machine learning",
    "deep learning", "artificial intelligence", "data analysis", "statistics", "llm", "transformers",
    # Databases
    "postgresql", "postgres", "mysql", "sqlite", "mongodb", "redis", "elasticsearch", "oracle", "dynamodb",
    # Tools, DevOps & Cloud
    "git", "github", "gitlab", "docker", "kubernetes", "aws", "azure", "gcp", "linux", "unix",
    "ci/cd", "rest api", "restful api", "graphql", "pytest", "unit testing", "celery", "postman", "nginx",
    # Methodologies & Concepts
    "agile", "scrum", "object oriented programming", "oop", "problem solving", "system design",
    "data structures", "algorithms", "microservices", "web scraping", "beautifulsoup", "selenium"
]

def extract_text_from_pdf(pdf_path):
    """Safely extracts text from a PDF file."""
    text = ""
    if not PdfReader:
        print("No PDF Reader library available (PyPDF2 or pypdf)")
        return ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text.strip()

def extract_contact_info(text, filename=""):
    """Extracts email, phone number, and candidate name heuristic."""
    # Email regex
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else "N/A"

    # Phone regex
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    phone = phone_match.group(0) if phone_match else "N/A"

    # Candidate Name heuristic (filename or first clean line)
    clean_filename = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
    # Remove bracketed numbers like (1) from filename
    clean_filename = re.sub(r'\s*\(\d+\)', '', clean_filename).strip()
    
    candidate_name = clean_filename if clean_filename and len(clean_filename) > 1 else "Candidate"
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        for line in lines[:3]:
            words = line.split()
            if 1 < len(words) <= 3 and all(w.isalpha() for w in words) and len(line) < 30:
                if not any(kw in line.lower() for kw in ["resume", "curriculum", "page", "education", "experience", "profile"]):
                    candidate_name = line.title()
                    break

    return candidate_name, email, phone

def extract_skills(text):
    """Extracts skills using combination of NLP POS tagging and dictionary phrase matching."""
    text_lower = text.lower()
    found_skills = set()

    # 1. Known phrase and keyword matching
    for skill in KNOWN_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill.title())

    # 2. spaCy POS tagging extraction for nouns/proper nouns if spaCy is available
    if nlp:
        try:
            doc = nlp(text)
            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"] and token.is_alpha and len(token.text) > 2:
                    t_lower = token.text.lower()
                    if t_lower in KNOWN_SKILLS:
                        found_skills.add(token.text.title())
        except Exception:
            pass

    return sorted(list(found_skills))

def calculate_similarity(job_text, resume_text):
    """Calculates TF-IDF Cosine Similarity percentage between Job Description and Resume."""
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([job_text, resume_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(similarity) * 100, 1)
    except Exception:
        return 0.0

def analyze_resume(job_desc, resume_text, filename=""):
    """
    Performs comprehensive analysis of a single resume against a job description.
    Returns detailed dictionary of match metrics, skills breakdown, contact info, and ATS feedback.
    """
    candidate_name, email, phone = extract_contact_info(resume_text, filename)
    job_skills = set(extract_skills(job_desc))
    resume_skills = set(extract_skills(resume_text))

    matched_skills = sorted(list(job_skills.intersection(resume_skills)))
    missing_skills = sorted(list(job_skills.difference(resume_skills)))
    extra_skills = sorted(list(resume_skills.difference(job_skills)))

    # Skill match score (0-100)
    if job_skills:
        skill_score = (len(matched_skills) / len(job_skills)) * 100
    else:
        skill_score = 0.0

    # TF-IDF contextual similarity score
    tfidf_score = calculate_similarity(job_desc, resume_text)

    # Weighted combined final score
    final_score = round(0.65 * skill_score + 0.35 * tfidf_score, 1)
    final_score = min(100.0, max(0.0, final_score))

    # ATS Feedback & Actionable Tips
    ats_feedback = []
    if final_score >= 80:
        ats_feedback.append("Excellent match! Resume covers key required technologies and context.")
    elif final_score >= 50:
        ats_feedback.append("Good match, but missing a few key technical skills required in the job description.")
    else:
        ats_feedback.append("Low match score. Resume needs optimization for this role's specific tech stack.")

    if missing_skills:
        ats_feedback.append(f"Consider highlighting missing skills such as: {', '.join(missing_skills[:5])}.")

    if len(resume_text.split()) < 150:
        ats_feedback.append("Resume length appears short. Ensure sufficient technical project detail is included.")

    return {
        "filename": filename,
        "name": candidate_name,
        "email": email,
        "phone": phone,
        "score": final_score,
        "skill_score": round(skill_score, 1),
        "tfidf_score": tfidf_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "all_resume_skills": sorted(list(resume_skills)),
        "ats_feedback": ats_feedback,
        "word_count": len(resume_text.split())
    }
