const API_URL =
    "https://resume-shortlisting-agent.onrender.com/review";


const resume = document.getElementById("resume");
const jobDescription = document.getElementById("jobDescription");

const resumeFile = document.getElementById("resumeFile");

const analyzeBtn = document.getElementById("analyzeBtn");

const loading = document.getElementById("loading");
const result = document.getElementById("result");
const errorBox = document.getElementById("error");


resumeFile.addEventListener("change", function () {

    const file = this.files[0];

    if (!file) {
        return;
    }

    const reader = new FileReader();

    reader.onload = function (event) {
        resume.value = event.target.result;
    };

    reader.readAsText(file);
});


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