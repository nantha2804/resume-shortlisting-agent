const API_URL =
    "https://resume-shortlisting-agent.onrender.com/review";


const resume = document.getElementById("resume");
const jobDescription = document.getElementById("jobDescription");

const resumeFile = document.getElementById("resumeFile");
const fileStatus = document.getElementById("fileStatus");

const analyzeBtn = document.getElementById("analyzeBtn");

const loading = document.getElementById("loading");
const result = document.getElementById("result");
const errorBox = document.getElementById("error");


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


    if (!resumeText || !jobText) {

        errorBox.textContent =
            "Please enter both Resume and Job Description.";

        errorBox.classList.remove("hidden");

        return;
    }


    errorBox.classList.add("hidden");
    result.classList.add("hidden");
    loading.classList.remove("hidden");

    analyzeBtn.disabled = true;


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
            })
        });


        if (!response.ok) {

            const errorData = await response.json();

            throw new Error(
                errorData.detail || "API request failed"
            );
        }


        const data = await response.json();


        document.getElementById("score").textContent =
            data.score;

        document.getElementById("decision").textContent =
            data.decision;


        displayList(
            "matchedSkills",
            data.matched_skills
        );

        displayList(
            "missingSkills",
            data.missing_skills
        );

        displayList(
            "strengths",
            data.strengths
        );

        displayList(
            "suggestions",
            data.suggestions
        );

        displayList(
            "keyPoints",
            data.key_points
        );


        result.classList.remove("hidden");

    } catch (error) {

        console.error(error);

        errorBox.textContent =
            "Error: " + error.message;

        errorBox.classList.remove("hidden");

    } finally {

        loading.classList.add("hidden");

        analyzeBtn.disabled = false;
    }

});


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