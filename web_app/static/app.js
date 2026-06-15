const state = {
  config: null,
  values: [],
};

const connection = document.getElementById("connection");
const camera = document.getElementById("camera");
const cameraUrl = document.getElementById("cameraUrl");
const cameraStatus = document.getElementById("cameraStatus");
const poses = document.getElementById("poses");
const sliders = document.getElementById("sliders");
const stats = document.getElementById("stats");
const log = document.getElementById("log");
const autoSend = document.getElementById("autoSend");
let manualTimer = null;

function writeLog(message) {
  const line = `${new Date().toLocaleTimeString()} ${message}`;
  log.textContent = `${line}\n${log.textContent}`.slice(0, 2000);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok || payload.ok === false) {
    throw new Error(payload.error || payload.response || response.statusText);
  }
  return payload;
}

async function sendManualMove(source = "Move") {
  try {
    const result = await api("/api/move", {
      method: "POST",
      body: JSON.stringify({ values: state.values }),
    });
    writeLog(`${source}: ${result.response}`);
    await refreshStatus();
  } catch (error) {
    writeLog(`${source} failed: ${error.message}`);
  }
}

function scheduleManualMove() {
  if (!autoSend.checked) {
    return;
  }
  window.clearTimeout(manualTimer);
  manualTimer = window.setTimeout(() => sendManualMove("Auto move"), 350);
}

function renderPoses() {
  poses.innerHTML = "";
  Object.keys(state.config.poses).forEach((name) => {
    const button = document.createElement("button");
    button.textContent = name.replace("_", " ");
    button.addEventListener("click", async () => {
      try {
        const result = await api("/api/pose", {
          method: "POST",
          body: JSON.stringify({ name }),
        });
        state.values = result.values;
        syncSliders();
        writeLog(`Pose ${name}: ${result.response}`);
        await refreshStatus();
      } catch (error) {
        writeLog(`Pose failed: ${error.message}`);
      }
    });
    poses.appendChild(button);
  });
}

function renderSliders() {
  sliders.innerHTML = "";
  state.config.joint_names.forEach((name, index) => {
    const [min, max] = state.config.joint_limits[name];
    const row = document.createElement("label");
    row.className = "slider-row";

    const title = document.createElement("span");
    title.textContent = name.replace("_", " ");

    const range = document.createElement("input");
    range.type = "range";
    range.min = min;
    range.max = max;
    range.value = state.values[index];
    range.dataset.index = index;

    const value = document.createElement("output");
    value.textContent = range.value;

    range.addEventListener("input", () => {
      state.values[index] = Number(range.value);
      value.textContent = range.value;
      scheduleManualMove();
    });

    row.append(title, range, value);
    sliders.appendChild(row);
  });
}

function syncSliders() {
  sliders.querySelectorAll("input").forEach((range) => {
    const index = Number(range.dataset.index);
    range.value = state.values[index];
    range.nextElementSibling.textContent = range.value;
  });
}

function renderStats(status) {
  stats.innerHTML = "";
  Object.entries(status).forEach(([key, value]) => {
    const dt = document.createElement("dt");
    dt.textContent = key;
    const dd = document.createElement("dd");
    dd.textContent = value;
    stats.append(dt, dd);
  });
}

async function refreshStatus() {
  try {
    const result = await api("/api/status");
    connection.textContent = `Connected to ${state.config.unoq_host}:${state.config.control_port}`;
    renderStats(result.status);
    if (result.status.target) {
      state.values = result.status.target.split(",").map(Number);
      syncSliders();
    }
  } catch (error) {
    connection.textContent = `Disconnected: ${error.message}`;
  }
}

async function init() {
  state.config = await api("/api/config");
  state.values = state.config.poses.ready.slice();
  camera.src = state.config.camera_url;
  cameraUrl.textContent = state.config.camera_url;
  cameraStatus.textContent = "If the image is blank, open the camera URL directly to see the UNO Q camera status.";
  camera.addEventListener("error", () => {
    cameraStatus.textContent = "Camera stream not available. Check the UNO Q app log and /dev/video camera path.";
  });
  renderPoses();
  renderSliders();
  await refreshStatus();
  setInterval(refreshStatus, 2000);
}

document.getElementById("sendBtn").addEventListener("click", async () => {
  await sendManualMove("Move");
});

document.getElementById("stopBtn").addEventListener("click", async () => {
  try {
    const result = await api("/api/stop", { method: "POST", body: "{}" });
    state.values = result.values;
    syncSliders();
    writeLog(`Rest: ${result.response}`);
  } catch (error) {
    writeLog(`Rest failed: ${error.message}`);
  }
});

document.getElementById("refreshBtn").addEventListener("click", refreshStatus);

init().catch((error) => {
  connection.textContent = `Startup failed: ${error.message}`;
});
