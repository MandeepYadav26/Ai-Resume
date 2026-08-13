import unittest
from resume_analyzer import extract_contact_info, extract_skills, calculate_similarity, analyze_resume

class TestResumeAnalyzer(unittest.TestCase):

    def test_extract_contact_info(self):
        sample_text = "John Doe\nEmail: john.doe@example.com\nPhone: (555) 123-4567"
        name, email, phone = extract_contact_info(sample_text, "john_doe_resume.pdf")
        self.assertEqual(email, "john.doe@example.com")
        self.assertEqual(phone, "(555) 123-4567")
        self.assertIn("John", name)

    def test_extract_skills(self):
        sample_text = "Experienced Python developer skilled in Flask, Docker, and PostgreSQL."
        skills = extract_skills(sample_text)
        self.assertIn("Python", skills)
        self.assertIn("Flask", skills)
        self.assertIn("Docker", skills)
        self.assertIn("Postgresql", skills)

    def test_calculate_similarity(self):
        job_desc = "Seeking a Python backend developer with Flask and SQL skills."
        resume_text = "Python software engineer experienced in Flask, REST APIs, and SQL databases."
        similarity = calculate_similarity(job_desc, resume_text)
        self.assertGreater(similarity, 0.0)

    def test_analyze_resume(self):
        job_desc = "Python developer needed for machine learning projects using Pandas and Scikit-Learn."
        resume_text = "Data scientist specializing in Python, Pandas, and Machine Learning."
        analysis = analyze_resume(job_desc, resume_text, "candidate_resume.pdf")
        self.assertIn("score", analysis)
        self.assertIn("matched_skills", analysis)
        self.assertGreater(analysis["score"], 0)

if __name__ == "__main__":
    unittest.main()
