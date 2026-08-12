# AI Resume Analyzer & Screening System

AI Resume Analyzer is a Flask-based web application designed to evaluate, rank, and screen candidate resumes against job descriptions. It uses Natural Language Processing (NLP), TF-IDF vectorization with cosine similarity, and keyword extraction to provide candidate matching scores, skill gap analysis, and ATS feedback.

## Features

- Bulk Resume Screening: Upload multiple PDF resumes simultaneously to evaluate and rank candidates.
- ATS Compatibility Check: Analyze individual resumes against job descriptions to receive feedback and match percentages.
- Contact Information Extraction: Automatically parses email addresses, phone numbers, and candidate names.
- Skill Match Analysis: Highlights matched skills, missing required skills, and additional resume skills.
- TF-IDF Cosine Similarity: Evaluates contextual and semantic alignment between job requirements and resume text.
- CSV Export: Automatically generates a structured `matched_candidates.csv` summary of screening results.

## Project Structure

```
Ai Resume/
├── app.py                  # Flask Web Application routes and API endpoints
├── resume_analyzer.py      # Core NLP, text parsing, and scoring logic
├── templates/
│   └── index.html          # Frontend dashboard user interface
├── static/                 # Static assets (CSS, JS, images)
├── uploads/                # Temporary directory for uploaded PDF files
├── matched_candidates.csv  # Auto-generated candidate summary export
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation
```

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Ai-Resume.git
   cd Ai-Resume
   ```

2. Create and activate a virtual environment:
   - On Windows:
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Download spaCy English model for enhanced NLP tagging:
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Running the Application

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## API Endpoints

- `GET /` : Serves the main web interface dashboard.
- `POST /api/screen` : Accepts a job description and multiple PDF resumes. Returns ranked candidates and analytics.
- `POST /api/ats-check` : Accepts a job description and single PDF resume. Returns ATS feedback and detailed match score.

## Technologies Used

- Backend: Python, Flask, Werkzeug
- Data Processing & NLP: PyPDF2 / pypdf, scikit-learn (TF-IDF), spaCy, Regular Expressions
- Frontend: HTML5, CSS3, JavaScript
