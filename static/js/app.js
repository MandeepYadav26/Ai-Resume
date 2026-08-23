document.addEventListener("DOMContentLoaded", () => {
    // Mode Tab Switcher
    const recruiterTab = document.getElementById("tab-recruiter");
    const jobseekerTab = document.getElementById("tab-jobseeker");
    const modeInput = document.getElementById("mode-input");
    const fileInput = document.getElementById("resumes-input");
    const dropzoneText = document.getElementById("dropzone-text");
    const submitBtnText = document.getElementById("submit-btn-text");
    const fileListDisplay = document.getElementById("file-list-display");

    let currentMode = "recruiter";

    recruiterTab.addEventListener("click", () => {
        currentMode = "recruiter";
        recruiterTab.classList.add("active");
        jobseekerTab.classList.remove("active");
        fileInput.setAttribute("multiple", "multiple");
        dropzoneText.innerText = "Drag & Drop PDF Resumes here, or click to browse (Multiple files allowed)";
        submitBtnText.innerText = "Match & Rank Candidates";
        fileListDisplay.innerText = "";
        fileInput.value = "";
    });

    jobseekerTab.addEventListener("click", () => {
        currentMode = "jobseeker";
        jobseekerTab.classList.add("active");
        recruiterTab.classList.remove("active");
        fileInput.removeAttribute("multiple");
        dropzoneText.innerText = "Drag & Drop your single PDF Resume here for ATS Check";
        submitBtnText.innerText = "Run ATS Compatibility Check";
        fileListDisplay.innerText = "";
        fileInput.value = "";
    });

    // Drag and Drop Handling
    const dropzone = document.getElementById("dropzone");

    dropzone.addEventListener("click", () => fileInput.click());

    ["dragenter", "dragover"].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add("dragover");
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove("dragover");
        });
    });

    dropzone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        updateFileList();
    });

    fileInput.addEventListener("change", updateFileList);

    function updateFileList() {
        if (fileInput.files.length > 0) {
            const fileNames = Array.from(fileInput.files).map(f => f.name).join(", ");
            fileListDisplay.innerText = `Selected (${fileInput.files.length}): ${fileNames}`;
        } else {
            fileListDisplay.innerText = "";
        }
    }

    // Form Submission
    const uploadForm = document.getElementById("analyzerForm");
    const spinner = document.getElementById("spinner");
    const submitBtn = document.getElementById("submit-btn");
    const resultsContainer = document.getElementById("results-container");
    const analyticsBar = document.getElementById("analytics-bar");

    uploadForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const jobDesc = document.getElementById("job-desc").value.strip ? document.getElementById("job-desc").value.strip() : document.getElementById("job-desc").value.trim();
        if (!jobDesc) {
            alert("Please enter a job description.");
            return;
        }

        if (!fileInput.files || fileInput.files.length === 0) {
            alert("Please upload at least one PDF resume.");
            return;
        }

        // Show Spinner
        spinner.style.display = "inline-block";
        submitBtn.disabled = true;

        const formData = new FormData();
        formData.append("job_description", jobDesc);

        let endpoint = "/api/screen";

        if (currentMode === "recruiter") {
            for (let i = 0; i < fileInput.files.length; i++) {
                formData.append("resumes", fileInput.files[i]);
            }
        } else {
            formData.append("resume", fileInput.files[0]);
            endpoint = "/api/ats-check";
        }

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok || data.error) {
                alert(data.error || "An error occurred while processing.");
                return;
            }

            if (currentMode === "recruiter") {
                renderRecruiterResults(data);
            } else {
                renderATSResults(data.analysis);
            }

        } catch (error) {
            console.error("Submission error:", error);
            alert("Failed to process request. Please check server connection.");
        } finally {
            spinner.style.display = "none";
            submitBtn.disabled = false;
        }
    });

    function getScoreColor(score) {
        if (score >= 75) return "#10b981"; // Emerald
        if (score >= 50) return "#3b82f6"; // Blue
        return "#ec4899"; // Pink
    }

    function renderRecruiterResults(data) {
        analyticsBar.style.display = "grid";
        document.getElementById("stat-total").innerText = data.analytics.total;
        document.getElementById("stat-avg").innerText = `${data.analytics.avg_score}%`;
        document.getElementById("stat-top").innerText = data.analytics.top_candidate;

        resultsContainer.innerHTML = "";

        const headerDiv = document.createElement("div");
        headerDiv.className = "results-header";
        headerDiv.innerHTML = `
            <h2>Candidate Rankings (${data.results.length})</h2>
            <button class="btn-export" onclick="window.location.href='/api/export-csv'">📥 Download CSV</button>
        `;
        resultsContainer.appendChild(headerDiv);

        data.results.forEach((c, index) => {
            const card = document.createElement("div");
            card.className = "candidate-card";
            const scoreColor = getScoreColor(c.score);

            const matchedBadges = c.matched_skills.map(s => `<span class="badge badge-matched">✓ ${s}</span>`).join("");
            const missingBadges = c.missing_skills.map(s => `<span class="badge badge-missing">✗ ${s}</span>`).join("");

            card.innerHTML = `
                <div class="candidate-top">
                    <div class="candidate-info">
                        <h3>#${index + 1} ${c.name}</h3>
                        <div class="candidate-meta">
                            <span> ${c.filename}</span>
                            <span> ${c.email}</span>
                            <span> ${c.phone}</span>
                        </div>
                    </div>
                    <div class="score-badge" style="--score-color: ${scoreColor}; --score-percent: ${c.score}%;">
                        ${c.score}%
                    </div>
                </div>

                <div class="skills-section">
                    <div class="skills-title">Matched Required Skills (${c.matched_skills.length})</div>
                    <div class="badges-wrapper">${matchedBadges || '<span class="badge">None detected</span>'}</div>
                </div>

                ${c.missing_skills.length > 0 ? `
                <div class="skills-section">
                    <div class="skills-title">Missing Required Skills (${c.missing_skills.length})</div>
                    <div class="badges-wrapper">${missingBadges}</div>
                </div>` : ''}

                <div class="feedback-box">
                    <strong>Feedback & Highlights:</strong>
                    <ul>
                        ${c.ats_feedback.map(f => `<li>${f}</li>`).join("")}
                    </ul>
                </div>
            `;
            resultsContainer.appendChild(card);
        });

        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    function renderATSResults(c) {
        analyticsBar.style.display = "none";
        resultsContainer.innerHTML = "";

        const scoreColor = getScoreColor(c.score);
        const matchedBadges = c.matched_skills.map(s => `<span class="badge badge-matched">✓ ${s}</span>`).join("");
        const missingBadges = c.missing_skills.map(s => `<span class="badge badge-missing">✗ ${s}</span>`).join("");

        const card = document.createElement("div");
        card.className = "candidate-card";
        card.innerHTML = `
            <h2>ATS Compatibility Report for ${c.name}</h2>
            <br>
            <div class="candidate-top">
                <div class="candidate-info">
                    <h3>Overall Match Breakdown</h3>
                    <div class="candidate-meta">
                        <span>Keyword Match: <strong>${c.skill_score}%</strong></span>
                        <span>Context Similarity: <strong>${c.tfidf_score}%</strong></span>
                        <span>Word Count: <strong>${c.word_count} words</strong></span>
                    </div>
                </div>
                <div class="score-badge" style="--score-color: ${scoreColor}; --score-percent: ${c.score}%;">
                    ${c.score}%
                </div>
            </div>

            <div class="skills-section">
                <div class="skills-title">Skills Present in Your Resume (${c.matched_skills.length})</div>
                <div class="badges-wrapper">${matchedBadges || '<span class="badge">No exact tech skills matched</span>'}</div>
            </div>

            <div class="skills-section">
                <div class="skills-title">Missing Skills to Add for ATS Pass (${c.missing_skills.length})</div>
                <div class="badges-wrapper">${missingBadges || '<span class="badge badge-matched">All required skills matched!</span>'}</div>
            </div>

            <div class="feedback-box">
                <strong>Actionable Recommendations:</strong>
                <ul>
                    ${c.ats_feedback.map(f => `<li>${f}</li>`).join("")}
                </ul>
            </div>
        `;
        resultsContainer.appendChild(card);
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }
});
