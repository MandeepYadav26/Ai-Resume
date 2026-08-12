import os
import csv
import uuid
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from resume_analyzer import extract_text_from_pdf, analyze_resume

app = Flask(__name__)

# Set upload folder within Ai Resume directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max upload limit

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/screen', methods=['POST'])
def screen_resumes():
    job_desc = request.form.get('job_description', '').strip()
    if not job_desc:
        return jsonify({"error": "Job description is required"}), 400

    files = request.files.getlist('resumes')
    if not files or files[0].filename == '':
        return jsonify({"error": "Please upload at least one PDF resume."}), 400

    results = []
    
    for file in files:
        if file and file.filename.lower().endswith('.pdf'):
            original_filename = secure_filename(file.filename) or "resume.pdf"
            unique_filename = f"{uuid.uuid4().hex[:8]}_{original_filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            try:
                file.save(save_path)
                resume_text = extract_text_from_pdf(save_path)
                
                if not resume_text:
                    results.append({
                        "filename": original_filename,
                        "name": original_filename,
                        "email": "N/A",
                        "phone": "N/A",
                        "score": 0.0,
                        "skill_score": 0.0,
                        "tfidf_score": 0.0,
                        "matched_skills": [],
                        "missing_skills": [],
                        "all_resume_skills": [],
                        "ats_feedback": ["Could not extract text from PDF. It may be scanned or empty."],
                        "word_count": 0
                    })
                else:
                    analysis = analyze_resume(job_desc, resume_text, original_filename)
                    results.append(analysis)
            except Exception as e:
                print(f"Error processing {original_filename}: {e}")
            finally:
                # Clean up uploaded temporary file to save disk space
                if os.path.exists(save_path):
                    try:
                        os.remove(save_path)
                    except Exception:
                        pass

    # Sort candidates by match score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    # Save evaluation summary to CSV inside Ai Resume directory
    csv_path = os.path.join(BASE_DIR, "matched_candidates.csv")
    try:
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Name", "Filename", "Score", "Email", "Phone", "Matched Skills", "Missing Skills"])
            writer.writeheader()
            for r in results:
                writer.writerow({
                    "Name": r["name"],
                    "Filename": r["filename"],
                    "Score": f"{r['score']}%",
                    "Email": r["email"],
                    "Phone": r["phone"],
                    "Matched Skills": ", ".join(r["matched_skills"]),
                    "Missing Skills": ", ".join(r["missing_skills"])
                })
    except Exception as e:
        print(f"Could not save CSV report: {e}")

    # Summary analytics
    total_candidates = len(results)
    avg_score = round(sum(r["score"] for r in results) / total_candidates, 1) if total_candidates > 0 else 0
    top_candidate = results[0]["name"] if results else "N/A"

    return jsonify({
        "success": True,
        "results": results,
        "analytics": {
            "total": total_candidates,
            "avg_score": avg_score,
            "top_candidate": top_candidate
        }
    })

@app.route('/api/ats-check', methods=['POST'])
def ats_check():
    job_desc = request.form.get('job_description', '').strip()
    if not job_desc:
        return jsonify({"error": "Job description is required"}), 400

    file = request.files.get('resume')
    if not file or file.filename == '' or not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Please upload a valid PDF resume."}), 400

    original_filename = secure_filename(file.filename) or "resume.pdf"
    unique_filename = f"{uuid.uuid4().hex[:8]}_{original_filename}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

    try:
        file.save(save_path)
        resume_text = extract_text_from_pdf(save_path)
        
        if not resume_text:
            return jsonify({"error": "Could not extract text from this PDF file. It might be scanned or image-based."}), 400

        analysis = analyze_resume(job_desc, resume_text, original_filename)
        return jsonify({"success": True, "analysis": analysis})
    except Exception as e:
        return jsonify({"error": f"Failed to analyze resume: {str(e)}"}), 500
    finally:
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except Exception:
                pass

if __name__ == '__main__':
    print("Starting AI Resume Server on http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)
