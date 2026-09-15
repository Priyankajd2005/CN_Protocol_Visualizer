let currentMode = "browsing";
let steps = [];
let currentStep = -1;
let timer = null;
let vizPlaying = false;

const $ = (id) => document.getElementById(id);

const labels = {
    browsing: "DNS → HTTP",
    mail: "SMTP",
    streaming: "DNS → HTTP Streaming"
};

function addLog(text) {
    const box = $("activityLog");
    const empty = box.querySelector(".empty");
    if (empty) empty.remove();

    const item = document.createElement("div");
    item.className = "log-item";
    item.innerHTML = `<time>${new Date().toLocaleTimeString()}</time>${escapeHtml(text)}`;
    box.prepend(item);
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

document.querySelectorAll(".tab").forEach(btn => {
    btn.addEventListener("click", () => switchMode(btn.dataset.mode));
});

function switchMode(mode) {
    currentMode = mode;
    document.querySelectorAll(".tab").forEach(b => b.classList.toggle("active", b.dataset.mode === mode));
    ["browsing", "mail", "streaming"].forEach(m => $(m + "Box").classList.toggle("hidden", m !== mode));
    resetVisualizer();
    addLog(`Selected ${mode}.`);
}

async function runActivity(activity, logText) {
    try {
        addLog(logText);
        const response = await fetch("/api/simulate", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({activity})
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Simulation failed");
        steps = data.steps;
        currentStep = 0;
        $("protocolName").textContent = labels[activity];
        $("statusDot").style.background = "#31d59b";
        $("statusDot").style.boxShadow = "0 0 14px #31d59b";
        enableControls();
        renderStep();
        startAutoReveal();
    } catch (err) {
        addLog("Error: " + err.message);
    }
}

$("visitBtn").addEventListener("click", () => {
    const url = $("urlInput").value.trim() || "https://example.com";
    addLog(`Visited ${url} (simulated).`);
    runActivity("browsing", `Browsing request started for ${url}.`);
});

$("sendBtn").addEventListener("click", () => {
    const to = $("toInput").value.trim() || "receiver@example.net";
    const subject = $("subjectInput").value.trim() || "Assignment Demo";
    addLog(`Email prepared for ${to} — "${subject}".`);
    runActivity("mail", `SMTP send started for ${to}.`);
});

$("playBtn").addEventListener("click", () => {
    const quality = $("qualitySelect").value;
    $("streamState").textContent = `Playing at ${quality} (simulated)`;
    addLog(`Streaming started at ${quality}.`);
    runActivity("streaming", `Stream started at ${quality}.`);
});

$("pauseBtn").addEventListener("click", () => {
    $("streamState").textContent = "Paused";
    addLog("Stream paused.");
    stopVizTimer();
});

function startAutoReveal() {
    stopVizTimer();
    vizPlaying = true;
    $("playVizBtn").textContent = "Ⅱ Pause";
    timer = setInterval(() => {
        if (currentStep < steps.length - 1) {
            currentStep++;
            renderStep();
        } else {
            stopVizTimer();
        }
    }, 1400);
}

function stopVizTimer() {
    if (timer) clearInterval(timer);
    timer = null;
    vizPlaying = false;
    $("playVizBtn").textContent = "▶ Play";
}

$("playVizBtn").addEventListener("click", () => {
    if (!steps.length) return;
    if (vizPlaying) stopVizTimer();
    else startAutoReveal();
});

$("nextBtn").addEventListener("click", () => {
    if (currentStep < steps.length - 1) {
        currentStep++;
        renderStep();
    }
});

$("prevBtn").addEventListener("click", () => {
    if (currentStep > 0) {
        currentStep--;
        renderStep();
    }
});

$("replayBtn").addEventListener("click", () => {
    if (!steps.length) return;
    stopVizTimer();
    currentStep = 0;
    renderStep();
    startAutoReveal();
});

function enableControls() {
    $("prevBtn").disabled = false;
    $("nextBtn").disabled = false;
    $("playVizBtn").disabled = false;
    $("replayBtn").disabled = false;
}

function resetVisualizer() {
    stopVizTimer();
    steps = [];
    currentStep = -1;
    $("protocolName").textContent = "Waiting";
    $("stepCounter").textContent = "Step 0 / 0";
    $("stepTitle").textContent = "Perform an activity to begin.";
    $("directionBadge").textContent = "—";
    $("timelineFill").style.width = "0%";
    $("stepCard").className = "step-card empty-card";
    $("stepCard").innerHTML = `<div class="empty-visual">
        <div class="big-network">↔</div>
        <h3>Protocol flow will appear here</h3>
        <p>The right panel updates when you perform the selected activity.</p>
    </div>`;
    $("prevBtn").disabled = true;
    $("nextBtn").disabled = true;
    $("playVizBtn").disabled = true;
    $("replayBtn").disabled = true;
}

function renderStep() {
    const s = steps[currentStep];
    if (!s) return;

    $("stepCounter").textContent = `Step ${currentStep + 1} / ${steps.length}`;
    $("stepTitle").textContent = s.title;
    $("directionBadge").textContent = s.direction;
    $("timelineFill").style.width = `${((currentStep + 1) / steps.length) * 100}%`;

    const arrow = s.direction.includes("→") ? "→" : "↔";

    $("stepCard").className = "step-card";
    $("stepCard").innerHTML = `
        <div class="step-top">
            <div class="step-type">${escapeHtml(s.type)}</div>
            <div class="time">${escapeHtml(s.time)}</div>
        </div>
        <h3>${escapeHtml(s.title)}</h3>
        <div class="arrow">${arrow}</div>
        <div class="message">${escapeHtml(s.message)}</div>
        <p><strong>Direction:</strong> ${escapeHtml(s.direction)}</p>
        <p><strong>Key fields:</strong> ${s.highlight.map(escapeHtml).join(" • ")}</p>
    `;
}

resetVisualizer();
