const API_URL =
    "https://resume-shortlisting-agent.onrender.com/review";


const resume = document.getElementById("resume");
const jobDescription = document.getElementById("jobDescription");

const resumeFile = document.getElementById("resumeFile");
const fileStatus = document.getElementById("fileStatus");

const analyzeBtn = document.getElementById("analyzeBtn");
const clearBtn = document.getElementById("clearBtn");
const downloadBtn = document.getElementById("downloadBtn");

const loading = document.getElementById("loading");
const progressMessage = document.getElementById("progressMessage");
const result = document.getElementById("result");
const errorBox = document.getElementById("error");
const scoreMeter = document.getElementById("scoreMeter");

let latestAnalysis = null;
let activeRequestController = null;


const MAX_FILE_SIZE = 5 * 1024 * 1024;
const SUPPORTED_EXTENSIONS = new Set([
    "txt", "pdf", "docx", "png", "jpg", "jpeg", "webp"
]);

if (window.pdfjsLib) {
    pdfjsLib.GlobalWorkerOptions.workerSrc =
        "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
}

resumeFile.addEventListener("change", async function () {
    const file = this.files[0];

    if (!file) {
        fileStatus.textContent = "";
        return;
    }

    const extension = file.name.split(".").pop().toLowerCase();

    if (!SUPPORTED_EXTENSIONS.has(extension)) {
        showFileError("Choose a TXT, PDF, DOCX, PNG, JPG, or WebP file.");
        this.value = "";
        return;
    }

    if (file.size > MAX_FILE_SIZE) {
        showFileError("The selected file is larger than 5 MB.");
        this.value = "";
        return;
    }

    errorBox.classList.add("hidden");
    fileStatus.textContent = `Reading ${file.name}...`;
    analyzeBtn.disabled = true;

    try {
        const extractedText = await extractResumeText(file, extension);

        if (!extractedText.trim()) {
            throw new Error("No text was found. Try a text-based PDF or a clearer image.");
        }

        resume.value = extractedText.trim();
        fileStatus.textContent = `Text loaded from ${file.name}.`;
    } catch (error) {
        showFileError(error.message || "Could not read this file.");
    } finally {
        analyzeBtn.disabled = false;
    }
});


async function extractResumeText(file, extension) {
    if (extension === "txt") {
        return file.text();
    }

    if (extension === "pdf") {
        if (!window.pdfjsLib) {
            throw new Error("PDF reader could not be loaded. Refresh the page and try again.");
        }

        const pdf = await pdfjsLib.getDocument({ data: await file.arrayBuffer() }).promise;
        const pages = [];

        for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber += 1) {
            const page = await pdf.getPage(pageNumber);
            const content = await page.getTextContent();
            pages.push(content.items.map((item) => item.str).join(" "));
        }

        return pages.join("\n");
    }

    if (extension === "docx") {
        if (!window.mammoth) {
            throw new Error("Word reader could not be loaded. Refresh the page and try again.");
        }

        const result = await mammoth.extractRawText({
            arrayBuffer: await file.arrayBuffer()
        });
        return result.value;
    }

    if (["png", "jpg", "jpeg", "webp"].includes(extension)) {
        if (!window.Tesseract) {
            throw new Error("Image text reader could not be loaded. Refresh the page and try again.");
        }

        const result = await Tesseract.recognize(file, "eng");
        return result.data.text;
    }

    throw new Error("This file type is not supported.");
}


function showFileError(message) {
    fileStatus.textContent = "";
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}


analyzeBtn.addEventListener("click", async function () {

    const resumeText = resume.value.trim();
    const jobText = jobDescription.value.trim();

    if (!resumeText && !jobText) {
        showError("Add resume text and a job description before analyzing.");
        return;
    }

    if (!resumeText) {
        showError("Add resume text or upload a supported resume file.");
        resume.focus();
        return;
    }

    if (!jobText) {
        showError("Add the job description you want to compare against.");
        jobDescription.focus();
        return;
    }

    clearError();
    result.classList.add("hidden");
    downloadBtn.disabled = true;
    loading.classList.remove("hidden");
    analyzeBtn.disabled = true;
    activeRequestController = new AbortController();
    progressMessage.textContent = "Sending resume and job description for analysis...";
    const progressTimer = window.setTimeout(() => {
        progressMessage.textContent = "The analysis service is still working. Please wait...";
    }, 1200);

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({
                resume: resumeText,
                job_description: jobText
            }),
            signal: activeRequestController.signal
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            const detail = errorData?.detail;
            const message = Array.isArray(detail)
                ? detail.map((item) => item.msg).join(" ")
                : detail;
            throw new Error(message || `The analysis service returned an error (${response.status}).`);
        }

        const data = await response.json();
        latestAnalysis = {
            ...data,
            analyzedAt: new Date(),
            resumeText,
            jobText
        };
        renderAnalysis(data);
        result.classList.remove("hidden");
    } catch (error) {
        if (error.name !== "AbortError") {
            console.error(error);
            showError(getAnalysisErrorMessage(error));
        }
    } finally {
        window.clearTimeout(progressTimer);
        loading.classList.add("hidden");
        analyzeBtn.disabled = false;
        activeRequestController = null;
    }
});


clearBtn.addEventListener("click", function () {
    activeRequestController?.abort();
    resume.value = "";
    jobDescription.value = "";
    resumeFile.value = "";
    fileStatus.textContent = "";
    latestAnalysis = null;
    result.classList.add("hidden");
    loading.classList.add("hidden");
    downloadBtn.disabled = true;
    document.getElementById("score").textContent = "0";
    document.getElementById("decision").textContent = "-";
    scoreMeter.style.setProperty("--score", "0%");
    scoreMeter.setAttribute("aria-valuenow", "0");
    clearError();
    resume.focus();
});


downloadBtn.addEventListener("click", function () {
    if (!latestAnalysis) {
        return;
    }

    const report = createReport(latestAnalysis);
    const reportBlob = new Blob([report], { type: "text/plain;charset=utf-8" });
    const downloadUrl = URL.createObjectURL(reportBlob);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = `resume-analysis-${new Date().toISOString().slice(0, 10)}.txt`;
    link.click();
    URL.revokeObjectURL(downloadUrl);
});


function renderAnalysis(data) {
    const score = Math.max(0, Math.min(100, Number(data.score) || 0));
    const scoreColor = score >= 80 ? "#27845c" : score >= 55 ? "#b87916" : "#bd4a43";

    document.getElementById("score").textContent = score;
    document.getElementById("decision").textContent = data.decision || "Not available";
    scoreMeter.style.setProperty("--score", `${score}%`);
    scoreMeter.style.setProperty("--score-color", scoreColor);
    scoreMeter.setAttribute("aria-valuenow", String(score));
    document.getElementById("decision").dataset.decision =
        (data.decision || "").toLowerCase().replaceAll(" ", "-");

    displayList("matchedSkills", data.matched_skills);
    displayList("missingSkills", data.missing_skills);
    displayList("strengths", data.strengths);
    displayList("suggestions", data.suggestions);
    displayList("keyPoints", data.key_points);
    downloadBtn.disabled = false;
}


function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}


function clearError() {
    errorBox.textContent = "";
    errorBox.classList.add("hidden");
}


function getAnalysisErrorMessage(error) {
    if (error instanceof TypeError) {
        return "Could not reach the analysis service. Check your connection and try again.";
    }

    return error.message || "The analysis could not be completed. Please try again.";
}


function createReport(data) {
    const formatList = (title, items) =>
        `${title}\n${items?.length ? items.map((item) => `- ${item}`).join("\n") : "- None"}`;

    return [
        "RESUME ANALYSIS REPORT",
        `Analyzed: ${data.analyzedAt.toLocaleString()}`,
        `Score: ${data.score}/100`,
        `Decision: ${data.decision}`,
        "",
        formatList("Matched skills", data.matched_skills),
        formatList("Missing skills", data.missing_skills),
        formatList("Strengths", data.strengths),
        formatList("Suggestions", data.suggestions),
        formatList("Key points", data.key_points),
        "",
        "Scoring is based on keyword matching and is intended as decision support, not an automated hiring decision."
    ].join("\n");
}


function displayList(elementId, items) {

    const element =
        document.getElementById(elementId);

    element.innerHTML = "";


    if (!items || items.length === 0) {

        const li = document.createElement("li");

        li.textContent = "None";

        element.appendChild(li);

        return;
    }


    items.forEach(function (item) {

        const li = document.createElement("li");

        li.textContent = item;

        element.appendChild(li);

    });
}