const form = document.querySelector("#generator-form");
const fileInput = document.querySelector("#document");
const fileLabel = document.querySelector("#file-label");
const dropZone = document.querySelector("#drop-zone");
const voiceSelect = document.querySelector("#voice");
const rate = document.querySelector("#rate");
const rateOutput = document.querySelector("#rate-output");
const generate = document.querySelector("#generate");
const prepareSample = document.querySelector("#prepare-sample");
const playSample = document.querySelector("#play-sample");
const sampleStatus = document.querySelector("#sample-status");
const sampleActions = document.querySelector("#sample-actions");
const progressCard = document.querySelector("#progress-card");
const progressBar = document.querySelector("#progress-bar");
const progressCount = document.querySelector("#progress-count");
const statusMessage = document.querySelector("#status-message");
const sectionName = document.querySelector("#section-name");
const results = document.querySelector("#results");
const fileList = document.querySelector("#file-list");
const favoriteVoices = ["Evan (Enhanced)", "Jamie (Premium)", "Samantha", "Daniel", "Karen", "Tessa (Enhanced)"];
let installedFavorites = [];
let previewId = null;

async function loadVoices() {
  try {
    const selectedVoice = voiceSelect.value;
    const response = await fetch("/api/voices", { cache: "no-store" });
    const data = await response.json();
    if (!data.voices?.length) return;
    const preferred = data.voices.includes(selectedVoice) ? selectedVoice :
      data.voices.includes("Evan (Enhanced)") ? "Evan (Enhanced)" :
      data.voices.includes("Samantha") ? "Samantha" : data.voices[0];
    installedFavorites = favoriteVoices.filter((voice) => data.voices.includes(voice));
    const remainingVoices = data.voices.filter((voice) => !installedFavorites.includes(voice));

    function voiceOption(voice) {
      const option = document.createElement("option");
      option.value = voice;
      option.textContent = voice;
      option.selected = voice === preferred;
      return option;
    }

    const recommendedGroup = document.createElement("optgroup");
    recommendedGroup.label = "Recommended for scholarly listening";
    recommendedGroup.append(...installedFavorites.map(voiceOption));
    const allGroup = document.createElement("optgroup");
    allGroup.label = "All other installed voices";
    allGroup.append(...remainingVoices.map(voiceOption));
    voiceSelect.replaceChildren(recommendedGroup, allGroup);
  } catch (_) {
    // Samantha remains available as the plain fallback.
  }
}

window.addEventListener("focus", loadVoices);

function showFile(file) {
  fileLabel.textContent = file ? file.name : "Call up your article";
  generate.disabled = !file;
  prepareSample.disabled = !file;
  invalidatePreparedSample();
}

fileInput.addEventListener("change", () => showFile(fileInput.files[0]));
rate.addEventListener("input", () => { rateOutput.textContent = `${rate.value} wpm`; });

function previewSelection() {
  fetch("/api/preview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ voice: voiceSelect.value, rate: Number(rate.value) }),
  }).catch(() => {});
}

function invalidatePreparedSample() {
  previewId = null;
  prepareSample.classList.remove("is-working");
  sampleActions.hidden = true;
  sampleStatus.textContent = "";
  if (fileInput.files[0]) prepareSample.disabled = false;
}

voiceSelect.addEventListener("change", () => {
  previewSelection();
  invalidatePreparedSample();
});
voiceSelect.addEventListener("keydown", (event) => {
  if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
  event.preventDefault();
  if (!installedFavorites.length) return;
  const current = installedFavorites.indexOf(voiceSelect.value);
  const next = current === -1
    ? (event.key === "ArrowRight" ? 0 : installedFavorites.length - 1)
    : Math.max(0, Math.min(installedFavorites.length - 1, current + (event.key === "ArrowRight" ? 1 : -1)));
  if (installedFavorites[next] === voiceSelect.value) return;
  voiceSelect.value = installedFavorites[next];
  voiceSelect.dispatchEvent(new Event("change"));
});
rate.addEventListener("change", () => {
  previewSelection();
  invalidatePreparedSample();
});

async function watchPreview(id) {
  const response = await fetch(`/api/previews/${id}`);
  const preview = await response.json();
  if (!response.ok) throw new Error(preview.error || "The sample could not be checked.");
  sampleStatus.textContent = preview.message;
  if (preview.status === "complete") {
    previewId = id;
    prepareSample.classList.remove("is-working");
    prepareSample.disabled = false;
    sampleActions.hidden = false;
    return;
  }
  if (preview.status === "error") throw new Error(preview.message);
  window.setTimeout(() => watchPreview(id).catch(showSampleError), 700);
}

function showSampleError(error) {
  sampleStatus.textContent = error.message;
  prepareSample.classList.remove("is-working");
  prepareSample.disabled = false;
}

prepareSample.addEventListener("click", async () => {
  if (!fileInput.files[0]) return;
  prepareSample.disabled = true;
  prepareSample.classList.add("is-working");
  sampleActions.hidden = true;
  sampleStatus.textContent = "Preparing your listening sample…";
  try {
    const response = await fetch("/api/previews", { method: "POST", body: new FormData(form) });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "The sample could not be started.");
    await watchPreview(result.preview_id);
  } catch (error) {
    showSampleError(error);
  }
});

playSample.addEventListener("click", async () => {
  if (!previewId) return;
  sampleStatus.textContent = "Playing through the Mac speakers…";
  try {
    const response = await fetch(`/api/previews/${previewId}/play`, { method: "POST" });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "The sample could not be played.");
  } catch (error) {
    showSampleError(error);
  }
});

["dragenter", "dragover"].forEach((eventName) => dropZone.addEventListener(eventName, (event) => {
  event.preventDefault();
  dropZone.classList.add("dragging");
}));
["dragleave", "drop"].forEach((eventName) => dropZone.addEventListener(eventName, (event) => {
  event.preventDefault();
  dropZone.classList.remove("dragging");
}));
dropZone.addEventListener("drop", (event) => {
  const file = event.dataTransfer.files[0];
  if (!file) return;
  const transfer = new DataTransfer();
  transfer.items.add(file);
  fileInput.files = transfer.files;
  showFile(file);
});

function renderFiles(files) {
  const audiobooks = files.filter((file) => file.name.endsWith(".m4b"));
  const packets = files.filter((file) => file.name.endsWith(".zip"));
  fileList.replaceChildren(...[...audiobooks, ...packets].map((file) => {
    const link = document.createElement("a");
    link.className = file.name.endsWith(".m4b") ? "file-link audiobook-link" : "file-link";
    link.href = file.url;
    link.download = file.name;
    const name = document.createElement("span");
    name.textContent = file.name.replace(/_/g, " ");
    const action = document.createElement("span");
    action.textContent = file.name.endsWith(".m4b") ? "Download audio only" : "Download PDF + audio packet";
    link.append(name, action);
    return link;
  }));
}

async function watchJob(jobId) {
  const response = await fetch(`/api/jobs/${jobId}`);
  const job = await response.json();
  if (!response.ok) throw new Error(job.error || "The job could not be checked.");
  statusMessage.textContent = job.message;
  sectionName.textContent = job.section && job.section !== "Complete" ? `Now rendering: ${job.section}` : "";
  const percent = job.total ? Math.round((job.current / job.total) * 100) : 4;
  progressBar.style.width = `${Math.max(4, percent)}%`;
  progressCount.textContent = job.total ? `${job.current} of ${job.total}` : "";
  if (job.status === "complete") {
    form.hidden = true;
    progressCard.hidden = true;
    results.hidden = false;
    renderFiles(job.files);
    return;
  }
  if (job.status === "error") throw new Error(job.message);
  window.setTimeout(() => watchJob(jobId).catch(showError), 900);
}

function showError(error) {
  statusMessage.textContent = "Something needs attention";
  sectionName.textContent = error.message;
  progressBar.style.width = "100%";
  progressBar.style.background = "#a84f43";
  generate.disabled = false;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!fileInput.files[0]) return;
  generate.disabled = true;
  results.hidden = true;
  progressCard.hidden = false;
  progressCard.scrollIntoView({ behavior: "smooth", block: "center" });
  progressBar.style.width = "4%";
  progressBar.style.background = "";
  statusMessage.textContent = "Starting…";
  sectionName.textContent = "Preparing the document locally";
  const data = new FormData(form);
  try {
    const response = await fetch("/api/jobs", { method: "POST", body: data });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "The listening packet could not be started.");
    await watchJob(result.job_id);
  } catch (error) {
    showError(error);
  }
});

document.querySelector("#start-over").addEventListener("click", () => {
  form.reset();
  fileInput.value = "";
  showFile();
  rateOutput.textContent = "130 wpm";
  form.hidden = false;
  results.hidden = true;
  progressCard.hidden = true;
  generate.disabled = true;
  invalidatePreparedSample();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

loadVoices();
