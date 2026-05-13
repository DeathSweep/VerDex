// Initialize elements for UI control
const fileInput = document.getElementById("fileInput");
const fileLabel = document.getElementById("fileLabel");
const modes = document.querySelectorAll(".mode");
const ResultTitle = document.getElementById("resultTitle")
const refreshbtn = document.getElementById("refresh");

// Initially file upload field is blank & default mode is selected at NER extraction
let selectedFile = null;
let selectedMode = "extract";

// Result Box is hidden at first
ResultTitle.classList.add("hidden");

// Logic for sending data -> flask Backend
function sendData() {
    if (!fileInput.files.length) {
        alert("Please upload a file");
        return;
    }

    const textBox = document.getElementById("textResult");
    textBox.textContent = "Processing... ⏳";
    textBox.classList.remove("hidden");

    // Packages file and selectedMode into an object called FormData
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("mode", selectedMode);

    // Stages the file upload to Flask Backend
    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        // When result is sent back from FB, showResult is called to display the received results.
        showResult(data); 
    })
    .catch(err => {
        console.error(err);
        alert("Something went wrong");
    });
}
function showResult(data){
    // Initialize elements for Result UI after processing PDF uploaded.
    const jsonBox = document.getElementById("jsonResult");
    const textBox = document.getElementById("textResult");
    const jsonBtn = document.getElementById("downloadJson");
    const pdfBtn = document.getElementById("downloadPdf");

    // Reset UI
    ResultTitle.classList.add("show");
    refreshbtn.classList.add("show");
    jsonBox.classList.add("hidden");
    textBox.classList.add("hidden");
    jsonBtn.classList.add("hidden");
    pdfBtn.classList.add("hidden");

    if (selectedMode === "extract") {
        const jsonData = JSON.stringify(data, null, 2);

        jsonBox.textContent = jsonData;
        jsonBox.classList.remove("hidden");
        jsonBtn.classList.remove("hidden");

        jsonBtn.onclick = () => {
            const blob = new Blob([jsonData], { type: "application/json" });
            const url = URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = url;
            a.download = "entities.json";
            a.click();
        };

    } else if (selectedMode === "translate") {

        // show success message instead of raw text
        textBox.textContent = data.message || "Translation complete!";
        textBox.classList.remove("hidden");

        pdfBtn.classList.remove("hidden");

        // Allows downloading of result PDF
        pdfBtn.onclick = () => {
            if (data.download) {
                window.open(data.download, "_blank");
            } else {
                alert("Download link missing");
            }
        };
    }
}

// File selection
fileInput.addEventListener("change", () => {
    selectedFile = fileInput.files[0];
    if (selectedFile) {
        fileLabel.textContent = selectedFile.name;
    }

    fileLabel.title = selectedFile.name;
});

// Mode toggle
modes.forEach(btn => {
    btn.addEventListener("click", () => {
        modes.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        selectedMode = btn.dataset.mode;
    });
});


const toggle = document.getElementById("themeToggle");

// Set correct icon on load
toggle.textContent = document.body.classList.contains("dark") ? "☀️" : "🌙";

toggle.addEventListener("click", () => {
    document.body.classList.toggle("dark");

    toggle.textContent = document.body.classList.contains("dark") ? "☀️" : "🌙";
});

refreshbtn.addEventListener("click", () => {
    location.reload();
});

// edit dictionary popup
const settingsBtn =
document.getElementById("dictSettingsBtn");

const popup =
    document.getElementById("dictionaryPopup");

const closeBtn =
    document.getElementById("closeDictionaryPopup");


// OPEN POPUP
settingsBtn.addEventListener("click", async () => {

    popup.classList.remove("hidden");

    await loadDictionary();
});

// CLOSE POPUP

closeBtn.addEventListener("click", () => {

    popup.classList.add("hidden");
});


// CLOSE ON OUTSIDE CLICK

window.addEventListener("click", (event) => {

    if (event.target === popup) {

        popup.classList.add("hidden");
    }
});

// =====================================================
// PAGINATION VARIABLES
// =====================================================

let dictionaryData = [];

let currentPage = 1;

const rowsPerPage = 20;


// =====================================================
// LOAD DICTIONARY
// =====================================================

async function loadDictionary() {

    try {

        const response =
            await fetch("/edit-dict");

        const data =
            await response.json();

        console.log(data);

        // Convert object to array
        dictionaryData =
            Object.entries(data);

        currentPage = 1;

        renderTable();

    } catch(error) {

        console.error(error);
    }
}


// =====================================================
// RENDER TABLE
// =====================================================

function renderTable() {

    const tableBody =
        document.getElementById(
            "dictionaryTableBody"
        );

    tableBody.innerHTML = "";

    // Calculate slice
    const start =
        (currentPage - 1) * rowsPerPage;

    const end =
        start + rowsPerPage;

    const pageData =
        dictionaryData.slice(start, end);

    // Render rows
    pageData.forEach(([word, details]) => {

        let translation = "";
        let type = "Base";

        // New format
        if (typeof details === "object") {

            translation =
                details.translation;

            type =
                details.type || "User";
        }

        // Old format
        else {

            translation = details;
        }

        const row =
            document.createElement("tr");

        row.innerHTML = `
            <td>${word}</td>

            <td>${translation}</td>

            <td>

                <span class="tag user-tag">
                    ${type}
                </span>

            </td>

            <td>

                <button
                    class="delete-btn"
                    data-word="${word}"
                >
                    Delete
                </button>

            </td>
        `;

        tableBody.appendChild(row);
    });

    // Update footer count
    document.getElementById(
        "dictionaryCount"
    ).textContent =
        `${dictionaryData.length} entries`;

    // Update page info
    const totalPages =
        Math.ceil(
            dictionaryData.length /
            rowsPerPage
        );

    document.getElementById(
        "pageInfo"
    ).textContent =
        `Page ${currentPage} of ${totalPages}`;

    attachDeleteEvents();
}


// =====================================================
// NEXT PAGE
// =====================================================

document.getElementById(
    "nextPageBtn"
).addEventListener("click", () => {

    const totalPages =
        Math.ceil(
            dictionaryData.length /
            rowsPerPage
        );

    if (currentPage < totalPages) {

        currentPage++;

        renderTable();
    }
});


// =====================================================
// PREVIOUS PAGE
// =====================================================

document.getElementById(
    "prevPageBtn"
).addEventListener("click", () => {

    if (currentPage > 1) {

        currentPage--;

        renderTable();
    }
});

function attachDeleteEvents() {

    const deleteButtons =
        document.querySelectorAll(".delete-btn");

    deleteButtons.forEach(button => {

        button.addEventListener("click", async () => {

            const word =
                button.dataset.word;

            await fetch("/delete-word", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    original: word
                })
            });

            loadDictionary();
        });
    });
}

document.getElementById("addWordBtn")
.addEventListener("click", async () => {

    const original =
        prompt("Original word:");

    const translation =
        prompt("Translation:");

    if (!original || !translation) {
        return;
    }

    await fetch("/add-word", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            original,
            translation,
            type: "User"
        })
    });

    loadDictionary();
});