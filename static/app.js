let currentMode = "browsing";
let steps = [];
let currentStep = -1;
let timer = null;
let vizPlaying = false;

const $ = (id) => document.getElementById(id);

const labels = {
    browsing: "DNS (UDP) + TCP + HTTP",
    mail: "DNS + TCP + SMTP",
    streaming: "DNS + TCP + HLS Streaming",
    transport: "TCP 3-Way Handshake & Teardown"
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
    ["browsing", "mail", "streaming", "transport"].forEach(m => {
        const box = $(m + "Box");
        if (box) box.classList.toggle("hidden", m !== mode);
    });
    resetVisualizer();
    addLog(`Switched mode to ${mode.toUpperCase()}.`);
}

async function runActivity(activity, logText) {
    try {
        addLog(logText);
        const includeTransport = $("includeTransportToggle") ? $("includeTransportToggle").checked : true;
        const response = await fetch("/api/simulate", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                activity: activity,
                include_transport: includeTransport
            })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Simulation failed");
        steps = data.steps;
        currentStep = 0;
        $("protocolName").textContent = labels[activity] || activity.toUpperCase();
        $("statusDot").style.background = "#31d59b";
        $("statusDot").style.boxShadow = "0 0 14px #31d59b";
        enableControls();
        renderStep();
        startAutoReveal();
    } catch (err) {
        addLog("Error: " + err.message);
    }
}

// 1. Browsing Visit
$("visitBtn").addEventListener("click", () => {
    const url = $("urlInput").value.trim() || "https://example.com";
    addLog(`Initiated visit to ${url}.`);
    runActivity("browsing", `Browsing trace started for ${url}.`);
});

// 2. Mail Send
$("sendBtn").addEventListener("click", () => {
    const to = $("toInput").value.trim() || "receiver@example.net";
    const subject = $("subjectInput").value.trim() || "Assignment Demo";
    addLog(`Mail drafted for ${to} - "${subject}".`);
    runActivity("mail", `SMTP mail transfer initiated for ${to}.`);
});

// 3. Streaming Controls
$("playBtn").addEventListener("click", () => {
    const quality = $("qualitySelect").value;
    $("streamState").textContent = `Streaming at ${quality}`;
    addLog(`Video stream started at ${quality}.`);
    runActivity("streaming", `HLS adaptive stream initiated at ${quality}.`);
});

$("pauseBtn").addEventListener("click", () => {
    $("streamState").textContent = "Paused";
    addLog("Stream paused by user.");
    stopVizTimer();
});

// 4. Transport Button
const runTransportBtn = $("runTransportBtn");
if (runTransportBtn) {
    runTransportBtn.addEventListener("click", () => {
        const src = $("srcPort").value || "54122";
        const dst = $("dstPort").value || "443";
        addLog(`Transport Layer simulation started (${src} -> ${dst}).`);
        runActivity("transport", `Running TCP 3-Way Handshake, Data & Teardown trace.`);
    });
}

function startAutoReveal() {
    stopVizTimer();
    vizPlaying = true;
    $("playVizBtn").textContent = "⏸ Pause";
    timer = setInterval(() => {
        if (currentStep < steps.length - 1) {
            currentStep++;
            renderStep();
        } else {
            stopVizTimer();
        }
    }, 1300);
}

function stopVizTimer() {
    if (timer) clearInterval(timer);
    timer = null;
    vizPlaying = false;
    $("playVizBtn").textContent = "▶ Auto";
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
    $("directionBadge").textContent = "Idle";
    $("timelineFill").style.width = "0%";
    $("stepCard").className = "step-card empty-card";
    $("stepCard").innerHTML = `<div class="empty-visual">
        <div class="big-network">⚡</div>
        <h3>Protocol & Transport flow will appear here</h3>
        <p>The right panel updates when you perform an activity on the left.</p>
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

    const isClientToServer = s.direction.includes("Client ->");
    const arrow = isClientToServer ? "Client ──▶ Server" : "Server ──▶ Client";

    const tcpStateBadge = $("tcpStateBadge");
    if (tcpStateBadge && s.state) {
        tcpStateBadge.textContent = s.state;
        if (s.state === "ESTABLISHED") {
            tcpStateBadge.style.background = "#059669";
        } else if (s.state === "CLOSED") {
            tcpStateBadge.style.background = "#4b5563";
        } else {
            tcpStateBadge.style.background = "#2563eb";
        }
    }

    const isTcp = s.type.includes("TCP");
    const isDns = s.type.includes("DNS");
    let pillClass = "pill-app";
    if (isTcp) pillClass = "pill-tcp";
    if (isDns) pillClass = "pill-dns";

    let transportDetailsHtml = "";
    if (s.flags || s.ports) {
        transportDetailsHtml = `
            <div class="transport-meta-bar">
                <span><b>L4 Transport:</b> ${escapeHtml(s.flags || "TCP")}</span>
                <span><b>Ports:</b> <code>${escapeHtml(s.ports || "-")}</code></span>
                <span><b>Seq:</b> <code>${escapeHtml(s.seq || "-")}</code></span>
                <span><b>Ack:</b> <code>${escapeHtml(s.ack || "-")}</code></span>
                ${s.state ? `<span><b>State:</b> <b class="state-hl">${escapeHtml(s.state)}</b></span>` : ""}
            </div>
        `;
    }

    $("stepCard").className = "step-card";
    $("stepCard").innerHTML = `
        <div class="step-top">
            <div class="step-type ${pillClass}">${escapeHtml(s.type)}</div>
            <div class="time">${escapeHtml(s.time)}</div>
        </div>
        <h3>${escapeHtml(s.title)}</h3>
        <div class="arrow ${isClientToServer ? 'arrow-c2s' : 'arrow-s2c'}">${arrow}</div>
        ${transportDetailsHtml}
        <div class="message">${escapeHtml(s.message)}</div>
        <div class="step-footer">
            <p><strong>Layer:</strong> ${escapeHtml(s.layer || "Application Layer (L7)")}</p>
            <p><strong>Key fields:</strong> ${(s.highlight || []).map(h => `<span class="tag-hl">${escapeHtml(h)}</span>`).join(" ")}</p>
        </div>
    `;
}

resetVisualizer();
