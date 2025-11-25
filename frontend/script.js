// Modern Video Captioner - Enhanced JavaScript
const API_BASE = "http://localhost:8002";
let uploadedFilename = "";
let outputFilename = "";

// DOM Elements
const videoInput = document.getElementById("videoInput");
const uploadArea = document.getElementById("uploadArea");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");
const uploadProgress = document.getElementById("uploadProgress");

const captionBtn = document.getElementById("captionBtn");
const captionStatus = document.getElementById("captionStatus");
const captionProgress = document.getElementById("captionProgress");
const captionsBox = document.getElementById("captionsBox");

const styleSelect = document.getElementById("styleSelect");
const renderBtn = document.getElementById("renderBtn");
const renderStatus = document.getElementById("renderStatus");
const renderProgress = document.getElementById("renderProgress");

const previewSection = document.getElementById("previewSection");
const previewVideo = document.getElementById("previewVideo");
const downloadBtn = document.getElementById("downloadBtn");
const newVideoBtn = document.getElementById("newVideoBtn");

// Utility Functions
function showStatus(element, message, type = "info") {
  element.className = `status status-${type} show`;

  if (type === "loading") {
    element.innerHTML = `<div class="spinner"></div><span>${message}</span>`;
  } else {
    element.textContent = message;
  }
}

function hideStatus(element) {
  element.classList.remove("show");
}

function showProgress(element) {
  element.classList.add("show");
  const fill = element.querySelector(".progress-fill");
  fill.style.width = "0%";
  animateProgress(fill);
}

function hideProgress(element) {
  element.classList.remove("show");
}

function animateProgress(fill) {
  let width = 0;
  const interval = setInterval(() => {
    if (width >= 90) {
      clearInterval(interval);
    } else {
      width += Math.random() * 10;
      fill.style.width = Math.min(width, 90) + "%";
    }
  }, 200);
}

function completeProgress(element) {
  const fill = element.querySelector(".progress-fill");
  fill.style.width = "100%";
  setTimeout(() => hideProgress(element), 500);
}

// File Upload Handlers
uploadArea.addEventListener("click", () => videoInput.click());

uploadArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadArea.classList.add("dragover");
});

uploadArea.addEventListener("dragleave", () => {
  uploadArea.classList.remove("dragover");
});

uploadArea.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadArea.classList.remove("dragover");

  const files = e.dataTransfer.files;
  if (files.length > 0 && files[0].type === "video/mp4") {
    videoInput.files = files;
    handleFileSelect();
  } else {
    showStatus(uploadStatus, "Please drop a valid MP4 file", "error");
  }
});

videoInput.addEventListener("change", handleFileSelect);

function handleFileSelect() {
  const file = videoInput.files[0];
  if (file) {
    uploadBtn.disabled = false;
    showStatus(uploadStatus, `Selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`, "info");
  }
}

// Upload Video
uploadBtn.addEventListener("click", async () => {
  const file = videoInput.files[0];
  if (!file) {
    showStatus(uploadStatus, "Please select an MP4 file first", "error");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    uploadBtn.disabled = true;
    showStatus(uploadStatus, "Uploading video...", "loading");
    showProgress(uploadProgress);

    const response = await fetch(`${API_BASE}/upload-video`, {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (data.error) {
      throw new Error(data.error);
    }

    uploadedFilename = data.video_filename;
    completeProgress(uploadProgress);
    showStatus(uploadStatus, ` Upload successful! Ready to generate captions.`, "success");

    // Enable next step
    captionBtn.disabled = false;

  } catch (error) {
    hideProgress(uploadProgress);
    showStatus(uploadStatus, ` Upload failed: ${error.message}`, "error");
    uploadBtn.disabled = false;
  }
});

// Generate Captions
captionBtn.addEventListener("click", async () => {
  if (!uploadedFilename) {
    showStatus(captionStatus, "Please upload a video first", "error");
    return;
  }

  const language = document.getElementById("languageSelect").value;
  const formData = new FormData();
  formData.append("video_filename", uploadedFilename);
  if (language) {
    formData.append("language", language);
  }

  try {
    captionBtn.disabled = true;
    const langText = language ? `in ${language.toUpperCase()}` : "with auto-detect";
    showStatus(captionStatus, `Generating captions ${langText}... This may take a minute.`, "loading");
    showProgress(captionProgress);
    captionsBox.classList.remove("show");

    const response = await fetch(`${API_BASE}/auto-generate-captions`, {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (data.error) {
      throw new Error(data.error);
    }

    completeProgress(captionProgress);
    showStatus(captionStatus, ` Generated ${data.captions.length} caption segments!`, "success");

    // Display captions
    captionsBox.textContent = JSON.stringify(data.captions, null, 2);
    captionsBox.classList.add("show");

    // Enable next step
    renderBtn.disabled = false;

  } catch (error) {
    hideProgress(captionProgress);
    showStatus(captionStatus, ` Caption generation failed: ${error.message}`, "error");
    captionBtn.disabled = false;
  }
});

// Render Video
renderBtn.addEventListener("click", async () => {
  if (!uploadedFilename) {
    showStatus(renderStatus, "Please upload a video and generate captions first", "error");
    return;
  }

  const style = styleSelect.value;
  const formData = new FormData();
  formData.append("video_filename", uploadedFilename);
  formData.append("style", style);

  try {
    renderBtn.disabled = true;
    showStatus(renderStatus, "Rendering video with captions... This may take several minutes.", "loading");
    showProgress(renderProgress);

    const response = await fetch(`${API_BASE}/render`, {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (data.error) {
      throw new Error(data.error);
    }

    outputFilename = data.output_filename;
    const outputUrl = `${API_BASE}${data.output_path}`;

    completeProgress(renderProgress);
    showStatus(renderStatus, ` Video rendered successfully!`, "success");

    // Show preview section
    previewSection.style.display = "block";
    previewVideo.src = outputUrl;
    previewVideo.load();

    // Scroll to preview
    previewSection.scrollIntoView({ behavior: "smooth", block: "nearest" });

  } catch (error) {
    hideProgress(renderProgress);
    showStatus(renderStatus, ` Rendering failed: ${error.message}`, "error");
    renderBtn.disabled = false;
  }
});

// Download Video
downloadBtn.addEventListener("click", () => {
  if (outputFilename) {
    // Properly encode the filename for URL
    const encodedFilename = encodeURIComponent(outputFilename);
    window.open(`${API_BASE}/download/${encodedFilename}`, "_blank");
  }
});

// Process Another Video
newVideoBtn.addEventListener("click", () => {
  // Reset everything
  uploadedFilename = "";
  outputFilename = "";

  videoInput.value = "";
  uploadBtn.disabled = true;
  captionBtn.disabled = true;
  renderBtn.disabled = true;

  hideStatus(uploadStatus);
  hideStatus(captionStatus);
  hideStatus(renderStatus);

  captionsBox.classList.remove("show");
  captionsBox.textContent = "";

  previewSection.style.display = "none";
  previewVideo.src = "";

  // Scroll to top
  window.scrollTo({ top: 0, behavior: "smooth" });
});

// Initialize
console.log("🎬 Video Captioner initialized!");
console.log("API Base:", API_BASE);
