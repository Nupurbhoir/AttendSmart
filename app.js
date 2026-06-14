// AttendSmart State Engine & Backend API Integrator

// Backend Base URL (relative since served from the same origin)
const API_BASE = "";

// State Variables
let offlineQueue = JSON.parse(localStorage.getItem("attend_smart_queue")) || [];
let isOnline = true;
let simulatedHours = 8;
let simulatedMinutes = 55;
let sequenceId = 1000;

// --- AUTHENTICATION FLOWS ---
async function handleUserLogin() {
    const emailInput = document.getElementById("login-email");
    const passwordInput = document.getElementById("login-password");
    const errorBox = document.getElementById("auth-error-box");
    const errorMsg = document.getElementById("auth-error-msg");
    
    if (!emailInput || !passwordInput) return;

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    try {
        const response = await fetch(`${API_BASE}/api/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem("attend_smart_token", data.token);
            window.location.href = "dashboard.html";
        } else {
            errorBox.classList.remove("hidden");
            errorMsg.textContent = data.error || "Login failed.";
        }
    } catch (err) {
        errorBox.classList.remove("hidden");
        errorMsg.textContent = "Cannot connect to the backend server. Please verify server.py is running.";
        console.error("Login API Error:", err);
    }
}

function handleUserLogout() {
    localStorage.removeItem("attend_smart_token");
    window.location.href = "login.html";
}

// --- UTILITIES ---
function getFormattedSimulatedTime() {
    const hoursStr = String(simulatedHours).padStart(2, '0');
    const minutesStr = String(simulatedMinutes).padStart(2, '0');
    const ampm = simulatedHours >= 12 ? 'PM' : 'AM';
    const displayHours = simulatedHours % 12 || 12;
    return `${String(displayHours).padStart(2, '0')}:${minutesStr} ${ampm}`;
}

// --- API FETCH & DYNAMIC UI POPULATIONS ---

// 1. Fetch Students
async function fetchStudents() {
    try {
        const token = localStorage.getItem("attend_smart_token");
        const res = await fetch(`${API_BASE}/api/students`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.ok) {
            return await res.json();
        }
    } catch (e) {
        console.error("Fetch Students Error:", e);
    }
    return {};
}

// 2. Fetch Devices
async function fetchDevices() {
    try {
        const token = localStorage.getItem("attend_smart_token");
        const res = await fetch(`${API_BASE}/api/devices`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.ok) {
            return await res.json();
        }
    } catch (e) {
        console.error("Fetch Devices Error:", e);
    }
    return {};
}

// 3. Fetch logs and alerts
async function fetchLogsAndAlerts() {
    try {
        const token = localStorage.getItem("attend_smart_token");
        const [logsRes, alertsRes] = await Promise.all([
            fetch(`${API_BASE}/api/logs`, { headers: { "Authorization": `Bearer ${token}` } }),
            fetch(`${API_BASE}/api/alerts`, { headers: { "Authorization": `Bearer ${token}` } })
        ]);

        if (logsRes.ok && alertsRes.ok) {
            const logs = await logsRes.json();
            const alerts = await alertsRes.json();
            renderLogsAndAlerts(logs, alerts);
        }
    } catch (e) {
        console.error("Fetch Logs/Alerts Error:", e);
    }
}

// Render timeline logs and alerts
function renderLogsAndAlerts(logs, alerts) {
    const feed = document.getElementById("terminal-body");
    const notifList = document.getElementById("notification-list");

    // Render Timeline Activity Feed
    if (feed) {
        feed.innerHTML = "";
        logs.forEach(log => {
            const item = document.createElement("div");
            item.className = `activity-item ${log.category}-type`;
            
            let iconClass = "fa-solid fa-info";
            if (log.category === 'system') iconClass = "fa-solid fa-gear";
            else if (log.category === 'success') iconClass = "fa-solid fa-circle-check";
            else if (log.category === 'warning') iconClass = "fa-solid fa-clock";
            else if (log.category === 'error') iconClass = "fa-solid fa-triangle-exclamation";
            else if (log.category === 'kafka') iconClass = "fa-solid fa-arrows-split-up-and-left";
            else if (log.category === 'ingest') iconClass = "fa-solid fa-upload";

            item.innerHTML = `
                <div class="activity-icon-container">
                    <i class="${iconClass}"></i>
                </div>
                <div class="activity-content">
                    <span class="activity-time">${log.time}</span>
                    <p>${log.message}</p>
                </div>
            `;
            feed.appendChild(item);
        });
        feed.scrollTop = feed.scrollHeight;
    }

    // Render Parent SMS Logs
    if (notifList) {
        notifList.innerHTML = "";
        if (alerts.length === 0) {
            notifList.innerHTML = `
                <div class="notification-empty">
                    <i class="fa-solid fa-envelope-open"></i>
                    <p>No messages dispatched yet. Simulate late check-ins or low attendance rates to trigger warning alerts.</p>
                </div>
            `;
        } else {
            alerts.forEach(alertItem => {
                const notifItem = document.createElement("div");
                notifItem.className = "notif-item";
                notifItem.innerHTML = `
                    <div class="notif-avatar">
                        <i class="fa-solid fa-envelope"></i>
                    </div>
                    <div class="notif-details">
                        <div class="notif-meta">
                            <span class="notif-sender"><i class="fa-regular fa-paper-plane"></i> ${alertItem.sender}</span>
                            <span class="notif-time">${alertItem.time}</span>
                        </div>
                        <p class="notif-text">${alertItem.text}</p>
                    </div>
                `;
                notifList.insertBefore(notifItem, notifList.firstChild);
            });
        }
    }
}

// Update Dashboard Roster and Top Analytics metrics
async function updateDashboardUI() {
    const rosterBody = document.getElementById("roster-body");
    if (!rosterBody) return; // Not on dashboard page

    const studentsList = await fetchStudents();
    const devicesList = await fetchDevices();
    const totalSessions = 10;
    
    let totalPresent = 0;
    let totalLate = 0;
    let totalAbsent = 0;

    rosterBody.innerHTML = ""; // Clear existing rows

    // Draw students dynamically
    Object.keys(studentsList).forEach(sid => {
        const student = studentsList[sid];
        const attended = student.presents + student.lates;
        const rate = totalSessions > 0 ? (attended / totalSessions) * 100 : 0.0;
        
        const tr = document.createElement("tr");
        tr.id = `row-${sid}`;

        let statusClass = "status-good";
        let statusText = "Compliant";
        if (rate < 40.0) {
            statusClass = "status-danger";
            statusText = "Severe Drop";
            tr.className = "row-danger";
        } else if (rate < 75.0) {
            statusClass = "status-warning";
            statusText = "Low Attendance";
            tr.className = "row-warning";
        }

        tr.innerHTML = `
            <td class="student-name-cell">
                <div class="avatar ${student.avatarClass || 'av-indigo'}">${student.initials || 'S'}</div>
                <span class="s-name">${student.name}</span>
            </td>
            <td><code>${student.id}</code></td>
            <td>${totalSessions}</td>
            <td class="c-present">${student.presents}</td>
            <td class="c-late">${student.lates}</td>
            <td class="c-absent">${student.absents}</td>
            <td class="attendance-rate"><strong>${rate.toFixed(2)}%</strong></td>
            <td><span class="pill-badge ${statusClass}">${statusText}</span></td>
        `;

        rosterBody.appendChild(tr);

        // Aggregate statistics
        totalPresent += student.presents;
        totalLate += student.lates;
        totalAbsent += student.absents;
    });

    // Update metrics counts
    document.getElementById("metric-present").textContent = totalPresent;
    document.getElementById("metric-late").textContent = totalLate;
    document.getElementById("metric-absent").textContent = totalAbsent;

    // Update active devices status count
    let onlineDevices = 0;
    let totalDevicesCount = 0;
    Object.keys(devicesList).forEach(did => {
        totalDevicesCount++;
        if (devicesList[did].active) onlineDevices++;
    });
    document.getElementById("metric-active-devices").textContent = `${onlineDevices}/${totalDevicesCount} Online`;

    // Update sync pending badge indicator
    const syncBadge = document.getElementById("sync-pending-badge");
    const syncText = document.getElementById("sync-text");
    if (offlineQueue.length > 0) {
        syncBadge.classList.remove("hidden");
        syncText.innerHTML = `<i class="fa-solid fa-arrows-rotate"></i> ${offlineQueue.length} Sync Pending`;
    } else {
        syncBadge.classList.add("hidden");
    }

    // Load logs/alerts
    fetchLogsAndAlerts();
}

// Populate input selectors inside simulator.html
async function populateSimulatorSelectors() {
    const studentSelect = document.getElementById("student-select");
    const deviceSelect = document.getElementById("device-select");
    
    if (!studentSelect && !deviceSelect) return;

    const studentsList = await fetchStudents();
    const devicesList = await fetchDevices();

    if (studentSelect) {
        studentSelect.innerHTML = "";
        Object.keys(studentsList).forEach(sid => {
            const opt = document.createElement("option");
            opt.value = sid;
            opt.textContent = `${studentsList[sid].name} (${sid})`;
            studentSelect.appendChild(opt);
        });
    }

    if (deviceSelect) {
        deviceSelect.innerHTML = "";
        Object.keys(devicesList).forEach(did => {
            const opt = document.createElement("option");
            opt.value = did;
            opt.textContent = devicesList[did].name;
            deviceSelect.appendChild(opt);
        });
    }
}

// Draw configuration switches in devices.html
async function updateDevicesUI() {
    const container = document.getElementById("device-list-container");
    if (!container) return;

    const devicesList = await fetchDevices();
    const studentsList = await fetchStudents();

    container.innerHTML = "";
    Object.keys(devicesList).forEach(did => {
        const dev = devicesList[did];
        const row = document.createElement("div");
        row.className = "device-row";
        
        row.innerHTML = `
            <div class="device-details">
                <span class="dev-name">${dev.name}</span>
                <span class="dev-id">${dev.id} | Protocol: gRPC over HTTPS</span>
            </div>
            <div>
                <label class="switch">
                    <input type="checkbox" id="switch-${did}" ${dev.active ? 'checked' : ''} onchange="toggleDeviceStatus('${did}')">
                    <span class="switch-slider"></span>
                </label>
            </div>
        `;
        container.appendChild(row);
    });

    // Count commits
    let totalPresent = 0;
    let totalLate = 0;
    Object.keys(studentsList).forEach(sid => {
        totalPresent += studentsList[sid].presents;
        totalLate += studentsList[sid].lates;
    });
    const writeField = document.getElementById("telemetry-total-writes");
    if (writeField) {
        writeField.textContent = totalPresent + totalLate;
    }
}

// Handle reader switch toggles in devices.html
window.toggleDeviceStatus = async function(deviceId) {
    try {
        const token = localStorage.getItem("attend_smart_token");
        const res = await fetch(`${API_BASE}/api/devices/toggle`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ deviceId })
        });
        if (res.ok) {
            updateDevicesUI();
        }
    } catch (e) {
        console.error("Toggle Device Error:", e);
    }
};

// --- SIMULATION HANDLERS (SIMULATOR.HTML) ---
window.setSimulationTime = function(h, m) {
    simulatedHours = h;
    simulatedMinutes = m;
    
    document.querySelectorAll(".time-btn").forEach(btn => btn.classList.remove("active"));
    
    if (h === 8 && m === 55) {
        document.getElementById("time-preset-present").classList.add("active");
        showTerminalAlert(`Simulation clock shifted to 08:55 AM (Arrival window)`, "success");
    } else if (h === 9 && m === 20) {
        document.getElementById("time-preset-late").classList.add("active");
        showTerminalAlert(`Simulation clock shifted to 09:20 AM (Late window)`, "success");
    } else if (h === 10 && m === 45) {
        document.getElementById("time-preset-outside").classList.add("active");
        showTerminalAlert(`Simulation clock shifted to 10:45 AM (Class completed)`, "success");
    }
    
    document.getElementById("live-clock").textContent = getFormattedSimulatedTime();
};

// Show temporary status box alerts below form in simulator.html
function showTerminalAlert(message, type="info") {
    const alertBox = document.getElementById("checkin-alert-box");
    const alertMsg = document.getElementById("checkin-alert-msg");
    
    if (!alertBox) return;

    alertBox.className = `alert-box ${type}`;
    alertBox.classList.remove("hidden");
    
    // Choose icon
    let iconClass = "fa-solid fa-circle-info";
    if (type === "success") iconClass = "fa-solid fa-circle-check";
    else if (type === "error") iconClass = "fa-solid fa-circle-exclamation";
    else if (type === "warning") iconClass = "fa-solid fa-triangle-exclamation";

    alertBox.innerHTML = `<i class="${iconClass}"></i> <span>${message}</span>`;
}

// Student onboarding handler on devices.html
async function handleStudentOnboard() {
    const idInput = document.getElementById("student-id");
    const nameInput = document.getElementById("student-name");
    const emailInput = document.getElementById("student-email");
    const parentEmailInput = document.getElementById("parent-email");
    const successBox = document.getElementById("onboard-success-box");

    const studentId = idInput.value.trim();
    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    const parentEmail = parentEmailInput.value.trim();

    try {
        const token = localStorage.getItem("attend_smart_token");
        const res = await fetch(`${API_BASE}/api/students/onboard`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ studentId, name, email, parentEmail })
        });
        
        const data = await res.json();
        
        if (res.ok) {
            successBox.classList.remove("hidden");
            idInput.value = "";
            nameInput.value = "";
            emailInput.value = "";
            parentEmailInput.value = "";
            
            setTimeout(() => {
                successBox.classList.add("hidden");
            }, 4000);

            updateDevicesUI();
        } else {
            alert(data.error || "Onboard failed.");
        }
    } catch (e) {
        console.error("Student Onboard Error:", e);
    }
}

// Ingest button handler on simulator.html
async function handleIngestCheckIn() {
    const studentSelect = document.getElementById("student-select");
    const studentId = studentSelect.value;
    const scheduleId = document.getElementById("schedule-select").value;
    const deviceId = document.getElementById("device-select").value;
    const status = document.getElementById("input-status").value;
    const method = document.getElementById("input-method").value;
    const timeString = `${String(simulatedHours).padStart(2, '0')}:${String(simulatedMinutes).padStart(2, '0')}`;

    const payload = { studentId, scheduleId, deviceId, status, method, timeString };

    if (isOnline) {
        // ONLINE FLOW
        try {
            const token = localStorage.getItem("attend_smart_token");
            const res = await fetch(`${API_BASE}/api/checkin`, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            
            if (res.ok && data.success) {
                showTerminalAlert(`Check-in logged successfully! Status: ${data.status}`, "success");
            } else {
                showTerminalAlert(`Check-in rejected: ${data.reason || "Validation failure"}`, "error");
            }
        } catch (e) {
            showTerminalAlert("Network connection error to backend server.", "error");
            console.error("Check-in Error:", e);
        }
    } else {
        // OFFLINE FLOW
        sequenceId++;
        const queueItem = {
            ...payload,
            sequence: sequenceId,
            timestamp: getFormattedSimulatedTime()
        };
        offlineQueue.push(queueItem);
        localStorage.setItem("attend_smart_queue", JSON.stringify(offlineQueue));
        
        showTerminalAlert(`Buffered check-in in SQLite device cache (Log ID: ${sequenceId}).`, "warning");
        updateSyncPillsUI();
    }
}

// Update header badges online/offline UI
function updateSyncPillsUI() {
    const syncBadge = document.getElementById("sync-pending-badge");
    const syncText = document.getElementById("sync-text");
    if (!syncBadge) return;

    if (offlineQueue.length > 0) {
        syncBadge.classList.remove("hidden");
        syncText.innerHTML = `<i class="fa-solid fa-arrows-rotate"></i> ${offlineQueue.length} Sync Pending`;
    } else {
        syncBadge.classList.add("hidden");
    }
}

// Toggle Offline/Online mode on simulator.html
async function toggleSimulatorOfflineMode() {
    isOnline = !isOnline;
    const btn = document.getElementById("network-toggle-btn");
    const statusPill = document.getElementById("connection-status");
    const statusText = document.getElementById("connection-text");

    if (isOnline) {
        // Return online
        btn.className = "btn btn-secondary btn-sm";
        btn.innerHTML = `<i class="fa-solid fa-wifi"></i> Toggle Reader Offline`;
        
        if (statusPill) statusPill.className = "status-pill online";
        if (statusText) statusText.innerHTML = `<i class="fa-solid fa-cloud"></i> Cloud Connected`;
        
        showTerminalAlert("Reader connection restored. Starting batch synchronization...", "info");
        
        // Batch sync queue
        if (offlineQueue.length > 0) {
            const logsToProcess = [...offlineQueue];
            offlineQueue = [];
            localStorage.setItem("attend_smart_queue", JSON.stringify(offlineQueue));
            updateSyncPillsUI();
            
            for (let i = 0; i < logsToProcess.length; i++) {
                const log = logsToProcess[i];
                await new Promise(resolve => setTimeout(resolve, 800)); // Sync spacing delay
                try {
                    const token = localStorage.getItem("attend_smart_token");
                    const res = await fetch(`${API_BASE}/api/checkin`, {
                        method: "POST",
                        headers: { 
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${token}`
                        },
                        body: JSON.stringify(log)
                    });
                    const data = await res.json();
                    if (res.ok && data.success) {
                        showTerminalAlert(`Sync resolved: Ingested ID ${log.sequence} (${log.studentId}) successfully.`, "success");
                    } else {
                        showTerminalAlert(`Sync error: ID ${log.sequence} rejected in validation check.`, "error");
                    }
                } catch (e) {
                    console.error("Sync batch item error:", e);
                }
            }
            showTerminalAlert("Batch synchronization completed successfully.", "success");
        }
    } else {
        // Go offline
        btn.className = "btn btn-secondary btn-sm offline-active";
        btn.innerHTML = `<i class="fa-solid fa-toggle-off"></i> Reader Offline`;
        
        if (statusPill) statusPill.className = "status-pill offline";
        if (statusText) statusText.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Network Offline`;
        
        showTerminalAlert("Scanning hardware disconnected from cloud. Buffered in local cache.", "warning");
    }
}

// --- INITIALIZATION ---
document.addEventListener("DOMContentLoaded", () => {
    const path = window.location.pathname;

    // Check if dashboard.html
    if (path.includes("dashboard.html")) {
        updateDashboardUI();
        
        // Roster polling or reset
        const resetBtn = document.getElementById("reset-analytics");
        if (resetBtn) {
            resetBtn.addEventListener("click", async () => {
                const token = localStorage.getItem("attend_smart_token");
                const res = await fetch(`${API_BASE}/api/reset`, { 
                    method: "POST",
                    headers: { "Authorization": `Bearer ${token}` }
                });
                if (res.ok) {
                    updateDashboardUI();
                }
            });
        }
        
        const downloadBtn = document.getElementById("download-report-btn");
        if (downloadBtn) {
            downloadBtn.addEventListener("click", () => {
                const token = localStorage.getItem("attend_smart_token");
                window.location.href = `${API_BASE}/api/reports/download?token=${token}`;
            });
        }
        
        const clearBtn = document.getElementById("clear-terminal");
        if (clearBtn) {
            clearBtn.addEventListener("click", () => {
                const term = document.getElementById("terminal-body");
                if (term) term.innerHTML = "";
            });
        }

        // Live refresh interval for feed updates
        setInterval(updateDashboardUI, 3000);
    }

    // Check if simulator.html
    if (path.includes("simulator.html")) {
        populateSimulatorSelectors();
        
        const ingestBtn = document.getElementById("ingest-btn");
        if (ingestBtn) {
            ingestBtn.addEventListener("click", handleIngestCheckIn);
        }

        const netToggle = document.getElementById("network-toggle-btn");
        if (netToggle) {
            netToggle.addEventListener("click", toggleSimulatorOfflineMode);
        }

        updateSyncPillsUI();
        document.getElementById("live-clock").textContent = getFormattedSimulatedTime();
    }

    // Check if devices.html
    if (path.includes("devices.html")) {
        updateDevicesUI();
        
        // Live telemetry updater
        setInterval(updateDevicesUI, 3000);
    }
});
