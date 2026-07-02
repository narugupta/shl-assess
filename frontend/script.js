/*
==========================================================
SHL Assessment Recommendation Frontend
==========================================================
*/

const API_URL = "/recommend";

// ----------------------------------------------------------
// Elements
// ----------------------------------------------------------

const queryInput = document.getElementById("query");

const recommendBtn = document.getElementById("recommendBtn");
const clearBtn = document.getElementById("clearBtn");

const loading = document.getElementById("loading");
const errorBox = document.getElementById("error");

const summary = document.getElementById("summary");
const summaryText = document.getElementById("summaryText");

const recommendations = document.getElementById("recommendations");
const recommendationList = document.getElementById("recommendationList");

// ----------------------------------------------------------
// Helpers
// ----------------------------------------------------------

function showLoading() {
    loading.classList.remove("hidden");
}

function hideLoading() {
    loading.classList.add("hidden");
}

function hideError() {
    errorBox.classList.add("hidden");
}

function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}

function clearResults() {

    summary.classList.add("hidden");
    recommendations.classList.add("hidden");

    summaryText.textContent = "";

    recommendationList.innerHTML = "";

    hideError();
}

// ----------------------------------------------------------
// Recommendation Card
// ----------------------------------------------------------

function createCard(rec) {

    const duration =
        rec.duration !== null && rec.duration !== undefined
            ? `${rec.duration} minutes`
            : "N/A";

    const languages =
        rec.languages.length > 0
            ? rec.languages.join(", ")
            : "N/A";

    const jobLevels =
        rec.job_levels.length > 0
            ? rec.job_levels.join(", ")
            : "N/A";

    const categories =
        rec.categories.length > 0
            ? rec.categories.join(", ")
            : "N/A";

    const confidence =
        `${(rec.confidence * 100).toFixed(0)}% Match`;

    return `
    <div class="recommendation-card">

        <h3>
            ${rec.rank}. ${rec.name}
        </h3>

        <p>
            <strong>Reason:</strong><br>
            ${rec.reason}
        </p>

        <p>
            <strong>Duration:</strong>
            ${duration}
        </p>

        <p>
            <strong>Languages:</strong>
            ${languages}
        </p>

        <p>
            <strong>Job Levels:</strong>
            ${jobLevels}
        </p>

        <p>
            <strong>Categories:</strong>
            ${categories}
        </p>

        <span class="confidence">

            ${confidence}

        </span>

        <br>

        <a
            class="assessment-link"
            href="${rec.url}"
            target="_blank"
            rel="noopener noreferrer"
        >
            Open SHL Assessment
        </a>

    </div>
    `;
}

// ----------------------------------------------------------
// API Call
// ----------------------------------------------------------

async function recommend() {

    const query = queryInput.value.trim();

    if (!query) {

        showError("Please enter a hiring requirement.");

        return;
    }

    clearResults();

    showLoading();

    try {

        const response = await fetch(API_URL, {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                query: query,

                conversation_history: [],

                top_k: 5

            })

        });

        if (!response.ok) {

            const text = await response.text();

            throw new Error(text);
        }

        const data = await response.json();

        hideLoading();

        summary.classList.remove("hidden");

        summaryText.textContent = data.message;

        recommendationList.innerHTML = "";

        if (
            data.recommendations &&
            data.recommendations.length > 0
        ) {

            data.recommendations.forEach(rec => {

                recommendationList.innerHTML += createCard(rec);

            });

            recommendations.classList.remove("hidden");

        }

    }
    catch (err) {

        hideLoading();

        showError(

            err.message ||

            "Unable to contact the server."

        );

    }

}

// ----------------------------------------------------------
// Events
// ----------------------------------------------------------

recommendBtn.addEventListener(

    "click",

    recommend

);

clearBtn.addEventListener(

    "click",

    () => {

        queryInput.value = "";

        clearResults();

    }

);

// Ctrl + Enter submits

queryInput.addEventListener(

    "keydown",

    (event) => {

        if (

            event.ctrlKey &&

            event.key === "Enter"

        ) {

            recommend();

        }

    }

);

// ----------------------------------------------------------
// Initial State
// ----------------------------------------------------------

clearResults();