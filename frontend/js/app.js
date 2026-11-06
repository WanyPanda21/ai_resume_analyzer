
// =====================================
// AI RESUME ANALYZER - FRONTEND LOGIC
// =====================================

// Existing FastAPI backend.
// Frontend and backend use the same domain.

const API_BASE_URL = "";

// Get HTML elements.

const analysisForm = document.getElementById("analysis-form");

const resumeInput = document.getElementById("resume");

const jobDescriptionInput = document.getElementById("job-description");

const analyzeButton = document.getElementById("analyze-btn");

const buttonText = document.getElementById("button-text");

const buttonLoader = document.getElementById("button-loader");

const errorMessage = document.getElementById("error-message");

const resultsSection = document.getElementById("results-section");

const candidateTable = document.getElementById("candidate-table");


// =====================================
// HELPER FUNCTIONS
// =====================================

function createElement(tag, className, text) {

    const element = document.createElement(tag);

    if (className) {
        element.className = className;
    }

    if (text !== undefined) {
        element.textContent = String(text);
    }

    return element;
}


function showError(message) {

    errorMessage.textContent = message;

    errorMessage.classList.remove("hidden");
}


function hideError() {

    errorMessage.textContent = "";

    errorMessage.classList.add("hidden");
}


function setLoading(isLoading) {

    analyzeButton.disabled = isLoading;

    buttonLoader.classList.toggle("hidden", !isLoading);

    buttonText.textContent = isLoading
        ? "Analyzing Resume..."
        : "✦ Analyze My Resume";
}


function formatDate(dateValue) {

    if (!dateValue) {
        return "N/A";
    }

    const date = new Date(dateValue);

    if (Number.isNaN(date.getTime())) {
        return "N/A";
    }

    return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric"
    });
}


// =====================================
// PDF FILE VALIDATION
// =====================================

resumeInput.addEventListener("change", function () {

    hideError();

    const file = resumeInput.files[0];

    if (!file) {
        return;
    }

    const isPdf =
        file.name.toLowerCase().endsWith(".pdf") &&
        file.type === "application/pdf";

    if (!isPdf) {

        resumeInput.value = "";

        showError("Please select a valid PDF file.");

        return;
    }

    if (file.size > 5 * 1024 * 1024) {

        resumeInput.value = "";

        showError("PDF file must be smaller than 5 MB.");

        return;
    }

    document.getElementById("upload-title").textContent =
        file.name;

    document.getElementById("upload-description").textContent =
        `${(file.size / 1024 / 1024).toFixed(2)} MB · PDF selected`;

});


// =====================================
// JOB DESCRIPTION CHARACTER COUNT
// =====================================

jobDescriptionInput.addEventListener("input", function () {

    const count = jobDescriptionInput.value.length;

    document.getElementById("char-count").textContent =
        `${count} characters`;

});


// =====================================
// SUBMIT RESUME FOR ANALYSIS
// =====================================

analysisForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    hideError();

    const resume = resumeInput.files[0];

    const jobDescription = jobDescriptionInput.value.trim();

    // Validate resume.

    if (!resume) {

        showError("Please upload your resume.");

        return;
    }

    if (
        !resume.name.toLowerCase().endsWith(".pdf") ||
        resume.type !== "application/pdf"
    ) {

        showError("Only PDF files are supported.");

        return;
    }

    if (resume.size > 5 * 1024 * 1024) {

        showError("PDF file must be smaller than 5 MB.");

        return;
    }

    // Validate job description.

    if (jobDescription.length < 30) {

        showError(
            "Job description must contain at least 30 characters."
        );

        return;
    }

    // Prepare multipart form data.

    const formData = new FormData();

    formData.append("resume", resume);

    formData.append("job_description", jobDescription);

    setLoading(true);

    try {

        // Call existing FastAPI endpoint.

        const response = await fetch(
            `${API_BASE_URL}/resumes/analyze`,
            {
                method: "POST",
                body: formData
            }
        );

        const result = await response.json();

        if (!response.ok) {

            throw new Error(
                result.detail || "Resume analysis failed."
            );
        }

        // Display analysis results.

        displayAnalysisResults(result);

        // Update dashboard.

        await loadCandidates();

        // Scroll to report.

        resultsSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    } catch (error) {

        console.error("Analysis error:", error);

        showError(
            error.message || "Unable to analyze resume. Please try again."
        );

    } finally {

        setLoading(false);

    }

});


// =====================================
// DISPLAY ANALYSIS RESULTS
// =====================================

function displayAnalysisResults(data) {

    resultsSection.classList.remove("hidden");

    // Candidate name.

    document.getElementById("candidate-name").textContent =
        data.candidate_name || "Unknown Candidate";


    // Match percentage.

    const score = Math.max(
        0,
        Math.min(100, Number(data.match_percentage) || 0)
    );

    document.getElementById("match-percentage").textContent =
        `${score.toFixed(1)}%`;

    const degrees = score * 3.6;

    document.getElementById("score-circle").style.background =
        `conic-gradient(#6555d9 ${degrees}deg, #eceaf5 ${degrees}deg)`;


    // Experience match.

    document.getElementById("experience-match").textContent =
        `Experience Match: ${data.experience_match || "N/A"}`;


    // AI summary.

    document.getElementById("summary").textContent =
        data.summary || "No summary available.";


    // Category scores.

    displayCategoryScores(data.category_scores || {});


    // Matched skills.

    displaySkills(
        "matched-skills",
        data.matched_skills || [],
        "skill-tag",
        "No matched skills found."
    );


    // Missing skills.

    displaySkills(
        "missing-skills",
        data.missing_skills || [],
        "missing-tag",
        "No missing skills identified."
    );


    // Strengths.

    displayList(
        "strengths",
        data.strengths || [],
        "No strengths available."
    );


    // Improvement suggestions.

    displayList(
        "suggestions",
        data.improvement_suggestions || [],
        "No suggestions available."
    );


    // Analysis ID.

    document.getElementById("analysis-id").textContent =
        `Analysis ID: ${data.analysis_id || "N/A"}`;


    // Update latest match score.

    document.getElementById("latest-score").textContent =
        `${score.toFixed(1)}%`;

}


// =====================================
// DISPLAY CATEGORY SCORES
// =====================================

function displayCategoryScores(scores) {

    const container = document.getElementById("category-scores");

    container.replaceChildren();

    const entries = Object.entries(scores);

    if (entries.length === 0) {

        container.appendChild(
            createElement("p", "empty-state", "No category scores available.")
        );

        return;
    }

    entries.forEach(([category, value]) => {

        const score = Number(value);

        if (!Number.isFinite(score)) {
            return;
        }

        const safeScore = Math.max(0, Math.min(100, score));

        const item = createElement("div", "category-item");

        const info = createElement("div", "category-info");

        const name = createElement("span", "", category);

        const percentage = createElement(
            "strong",
            "",
            `${safeScore.toFixed(1)}%`
        );

        info.append(name, percentage);

        const track = createElement("div", "progress-track");

        const fill = createElement("div", "progress-fill");

        fill.style.width = `${safeScore}%`;

        track.appendChild(fill);

        item.append(info, track);

        container.appendChild(item);

    });

}


// =====================================
// DISPLAY SKILLS
// =====================================

function displaySkills(containerId, skills, className, emptyText) {

    const container = document.getElementById(containerId);

    container.replaceChildren();

    if (!Array.isArray(skills) || skills.length === 0) {

        container.appendChild(
            createElement("p", "empty-state", emptyText)
        );

        return;
    }

    skills.forEach(skill => {

        const tag = createElement(
            "span",
            className,
            skill
        );

        container.appendChild(tag);

    });

}


// =====================================
// DISPLAY STRENGTHS AND SUGGESTIONS
// =====================================

function displayList(containerId, items, emptyText) {

    const container = document.getElementById(containerId);

    container.replaceChildren();

    if (!Array.isArray(items) || items.length === 0) {

        container.appendChild(
            createElement("li", "", emptyText)
        );

        return;
    }

    items.forEach(item => {

        const listItem = createElement(
            "li",
            "",
            item
        );

        container.appendChild(listItem);

    });

}


// =====================================
// LOAD CANDIDATE HISTORY
// =====================================

async function loadCandidates() {

    candidateTable.replaceChildren();

    try {

        const response = await fetch(
            `${API_BASE_URL}/resumes?limit=50`
        );

        if (!response.ok) {

            throw new Error("Unable to load candidates.");
        }

        const candidates = await response.json();

        if (!Array.isArray(candidates)) {

            throw new Error("Invalid candidate response.");
        }

        // Update dashboard statistics.

        document.getElementById("total-resumes").textContent =
            candidates.length;

        document.getElementById("total-analyses").textContent =
            candidates.length;


        if (candidates.length === 0) {

            const row = createElement("tr");

            const cell = createElement(
                "td",
                "empty-state",
                "No candidates analyzed yet."
            );

            cell.colSpan = 4;

            row.appendChild(cell);

            candidateTable.appendChild(row);

            return;
        }

        // Display latest candidates first.

        candidates.sort((a, b) => {

            return new Date(b.created_at || 0) -
                   new Date(a.created_at || 0);

        });

        candidates.forEach(candidate => {

            const row = document.createElement("tr");

            const name = createElement(
                "td",
                "",
                candidate.candidate_name || "Unknown"
            );

            const email = createElement(
                "td",
                "",
                candidate.email || "N/A"
            );

            const experience = createElement(
                "td",
                "",
                `${candidate.years_experience ?? 0} years`
            );

            const date = createElement(
                "td",
                "",
                formatDate(candidate.created_at)
            );

            row.append(name, email, experience, date);

            candidateTable.appendChild(row);

        });

    } catch (error) {

        console.error("Candidate loading error:", error);

        const row = createElement("tr");

        const cell = createElement(
            "td",
            "empty-state",
            "Unable to load candidate history."
        );

        cell.colSpan = 4;

        row.appendChild(cell);

        candidateTable.appendChild(row);

    }

}


// =====================================
// REFRESH CANDIDATE HISTORY
// =====================================

document.getElementById("refresh-btn").addEventListener(
    "click",
    loadCandidates
);


// =====================================
// START NEW ANALYSIS
// =====================================

document.getElementById("new-analysis-btn").addEventListener(
    "click",
    function () {

        analysisForm.reset();

        resultsSection.classList.add("hidden");

        document.getElementById("upload-title").textContent =
            "Click to upload your resume";

        document.getElementById("upload-description").textContent =
            "PDF files only · Maximum size 5 MB";

        document.getElementById("char-count").textContent =
            "0 characters";

        hideError();

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    }
);


// =====================================
// INITIALIZE DASHBOARD
// =====================================

document.addEventListener("DOMContentLoaded", function () {

    loadCandidates();

});
