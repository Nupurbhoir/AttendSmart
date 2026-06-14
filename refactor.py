import os
import re

def update_html(filename, page_title, page_subtitle, active_nav, main_content_html):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Extract head
    head_match = re.search(r'(<head>.*?</head>)', content, re.DOTALL)
    head = head_match.group(1) if head_match else ""
    
    # We will replace the body entirely
    new_body = f"""<body class="light-theme">
    <div class="app-layout">
        <!-- SIDEBAR -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <div class="logo-icon"><i class="fa-solid fa-calendar-check"></i></div>
                <div class="logo-text">
                    <h1>AttendSmart</h1>
                </div>
            </div>
            
            <nav class="sidebar-nav">
                <a href="dashboard.html" class="nav-item {'active' if active_nav == 'dashboard' else ''}"><i class="fa-solid fa-chart-line"></i> <span>Dashboard</span></a>
                <a href="simulator.html" class="nav-item {'active' if active_nav == 'simulator' else ''}"><i class="fa-solid fa-fingerprint"></i> <span>Terminal</span></a>
                <a href="devices.html" class="nav-item {'active' if active_nav == 'devices' else ''}"><i class="fa-solid fa-microchip"></i> <span>Readers</span></a>
            </nav>
            
            <div class="sidebar-footer">
                <button onclick="handleUserLogout();" class="nav-btn-logout"><i class="fa-solid fa-right-from-bracket"></i> <span>Sign Out</span></button>
            </div>
        </aside>

        <!-- MAIN CONTENT -->
        <main class="main-wrapper">
            <header class="top-header">
                <div class="header-title">
                    <h2>{page_title}</h2>
                    <p>{page_subtitle}</p>
                </div>
                <div class="header-status">
                    <div id="connection-status" class="status-pill online">
                        <span class="status-dot"></span>
                        <span id="connection-text">Connected</span>
                    </div>
                    <div id="sync-pending-badge" class="status-pill pending hidden">
                        <span class="status-dot pulsing"></span>
                        <span id="sync-text">Syncing</span>
                    </div>
                    <div class="clock-area">
                        <i class="fa-regular fa-clock"></i>
                        <span id="live-clock">--:--:--</span>
                    </div>
                </div>
            </header>
            
            <div class="page-content slide-up-animation">
{main_content_html}
            </div>
        </main>
    </div>

    <!-- Script -->
    <script src="app.js"></script>
</body>"""

    new_content = f"<!DOCTYPE html>\n<html lang=\"en\">\n{head}\n{new_body}\n</html>"
    
    with open(filename, 'w') as f:
        f.write(new_content)

# DASHBOARD CONTENT
dashboard_main = """
                <!-- METRICS GRID -->
                <section class="metrics-grid">
                    <div class="metric-card metric-gradient-green">
                        <div class="metric-icon"><i class="fa-solid fa-circle-check"></i></div>
                        <div class="metric-info">
                            <span class="metric-label">Present Today</span>
                            <h3 id="metric-present">0</h3>
                        </div>
                    </div>
                    <div class="metric-card metric-gradient-orange">
                        <div class="metric-icon"><i class="fa-solid fa-clock"></i></div>
                        <div class="metric-info">
                            <span class="metric-label">Late Arrivals</span>
                            <h3 id="metric-late">0</h3>
                        </div>
                    </div>
                    <div class="metric-card metric-gradient-red">
                        <div class="metric-icon"><i class="fa-solid fa-circle-xmark"></i></div>
                        <div class="metric-info">
                            <span class="metric-label">Absent Students</span>
                            <h3 id="metric-absent">0</h3>
                        </div>
                    </div>
                    <div class="metric-card metric-gradient-blue">
                        <div class="metric-icon"><i class="fa-solid fa-server"></i></div>
                        <div class="metric-info">
                            <span class="metric-label">Active Readers</span>
                            <h3 id="metric-active-devices">0 Online</h3>
                        </div>
                    </div>
                </section>

                <div class="dashboard-analytics-layout mt-4">
                    <!-- LEFT COLUMN -->
                    <section class="analytics-column">
                        <div class="card">
                            <div class="card-header">
                                <h2><i class="fa-solid fa-users"></i> Course Roster & Attendance</h2>
                                <button id="reset-analytics" class="btn btn-secondary btn-sm"><i class="fa-solid fa-rotate-left"></i> Reset</button>
                            </div>
                            <div class="card-body no-padding table-responsive">
                                <table class="roster-table">
                                    <thead>
                                        <tr>
                                            <th>Student</th>
                                            <th>ID</th>
                                            <th>Sessions</th>
                                            <th>Present</th>
                                            <th>Late</th>
                                            <th>Absent</th>
                                            <th>Rate</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody id="roster-body"></tbody>
                                </table>
                            </div>
                        </div>
                    </section>

                    <!-- RIGHT COLUMN -->
                    <section class="analytics-column">
                        <div class="card">
                            <div class="card-header">
                                <h2><i class="fa-solid fa-list-check"></i> Live Stream Logs</h2>
                                <button id="clear-terminal" class="btn-clear"><i class="fa-solid fa-trash-can"></i></button>
                            </div>
                            <div id="terminal-body" class="activity-feed scrollable"></div>
                        </div>
                        <div class="card mt-4">
                            <div class="card-header">
                                <h2><i class="fa-solid fa-envelope"></i> Notifications</h2>
                            </div>
                            <div id="notification-list" class="notification-list scrollable"></div>
                        </div>
                    </section>
                </div>
"""

# SIMULATOR CONTENT
simulator_main = """
                <div class="simulator-layout-grid">
                    <div class="card simulator-terminal-card">
                        <div class="card-header">
                            <h2><i class="fa-solid fa-mobile-screen-button"></i> Check-In Simulator</h2>
                            <span class="badge highlight">Interactive</span>
                        </div>
                        
                        <div class="card-body">
                            <p class="card-desc">Simulate student check-ins. Watch the dashboard update in real-time.</p>
                            
                            <div id="checkin-alert-box" class="alert-box hidden">
                                <i class="fa-solid fa-circle-info"></i>
                                <span id="checkin-alert-msg">Ready.</span>
                            </div>

                            <form id="simulator-form" onsubmit="event.preventDefault();">
                                <div class="simulator-form-flex">
                                    <div class="sim-form-col">
                                        <div class="form-group">
                                            <label>Select Student</label>
                                            <select id="student-select" class="form-control"></select>
                                        </div>
                                        <div class="form-group">
                                            <label>Active Class</label>
                                            <select id="schedule-select" class="form-control">
                                                <option value="SCH_CS101">CS101 (09:00 - 10:30)</option>
                                                <option value="SCH_MATH201">MATH201 (11:00 - 12:30)</option>
                                            </select>
                                        </div>
                                        <div class="form-group">
                                            <label>Scanning Device</label>
                                            <select id="device-select" class="form-control"></select>
                                        </div>
                                    </div>

                                    <div class="sim-form-col">
                                        <div class="form-group">
                                            <div class="label-with-presets">
                                                <label>Location</label>
                                                <div class="preset-links">
                                                    <button type="button" class="preset-btn" onclick="setCoordinates(37.77492, -122.41942, 'Inside Classroom')">Inside</button>
                                                    <button type="button" class="preset-btn warning-preset" onclick="setCoordinates(37.76000, -122.41000, 'Outside Campus')">Outside</button>
                                                </div>
                                            </div>
                                            <div class="coordinate-inputs">
                                                <input type="number" id="input-lat" class="form-control" step="0.00001" value="37.77492">
                                                <input type="number" id="input-lon" class="form-control" step="0.00001" value="-122.41942">
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <div class="label-with-presets">
                                                <label>Biometric Match</label>
                                                <div class="preset-links">
                                                    <button type="button" class="preset-btn" onclick="setBiometric(0.95)">95%</button>
                                                    <button type="button" class="preset-btn error-preset" onclick="setBiometric(0.68)">68%</button>
                                                </div>
                                            </div>
                                            <div class="slider-container">
                                                <input type="range" id="biometric-score" class="form-range" min="0.50" max="1.00" step="0.01" value="0.92">
                                                <span id="biometric-value" class="slider-badge">92%</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div class="form-group mt-3">
                                    <label>Time Window</label>
                                    <div class="timestamp-presets">
                                        <button type="button" id="time-preset-present" class="time-btn active" onclick="setSimulationTime(8, 55)">
                                            <span class="time-btn-title">On Time</span>
                                            <span class="time-btn-sub">08:55 AM</span>
                                        </button>
                                        <button type="button" id="time-preset-late" class="time-btn" onclick="setSimulationTime(9, 20)">
                                            <span class="time-btn-title">Late</span>
                                            <span class="time-btn-sub">09:20 AM</span>
                                        </button>
                                        <button type="button" id="time-preset-outside" class="time-btn" onclick="setSimulationTime(10, 45)">
                                            <span class="time-btn-title">Out of Hours</span>
                                            <span class="time-btn-sub">10:45 AM</span>
                                        </button>
                                    </div>
                                </div>

                                <div class="simulator-offline-option mt-4">
                                    <span class="offline-opt-label">Reader Network Mode:</span>
                                    <button type="button" id="network-toggle-btn" class="btn btn-secondary btn-sm">
                                        <i class="fa-solid fa-wifi"></i> Toggle Offline
                                    </button>
                                </div>

                                <button type="button" id="ingest-btn" class="btn btn-primary btn-block btn-lg mt-4 shadow-btn">
                                    <i class="fa-solid fa-fingerprint"></i> Ingest Scan Event
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
"""

# DEVICES CONTENT
devices_main = """
                <div class="devices-layout-grid">
                    <div class="card onboarding-card">
                        <div class="card-header">
                            <h2><i class="fa-solid fa-user-plus"></i> Onboard Student</h2>
                        </div>
                        <div class="card-body">
                            <p class="card-desc">Register a new student profile. They will appear on the dashboard instantly.</p>
                            <div id="onboard-success-box" class="alert-box success hidden">
                                <i class="fa-solid fa-circle-check"></i> <span>Onboarded!</span>
                            </div>
                            <form id="onboard-form" onsubmit="event.preventDefault(); handleStudentOnboard();">
                                <div class="form-group">
                                    <label>Student ID Code</label>
                                    <input type="text" id="student-id" class="form-control" required placeholder="e.g. S104" pattern="S[0-9]{3,}">
                                </div>
                                <div class="form-group">
                                    <label>Full Name</label>
                                    <input type="text" id="student-name" class="form-control" required placeholder="e.g. Jane Doe">
                                </div>
                                <div class="form-group">
                                    <label>Student Email</label>
                                    <input type="email" id="student-email" class="form-control" required placeholder="jane@school.edu">
                                </div>
                                <div class="form-group">
                                    <label>Parent/Guardian Email</label>
                                    <input type="email" id="parent-email" class="form-control" required placeholder="parent@home.com">
                                </div>
                                <button type="submit" class="btn btn-primary btn-block mt-4 shadow-btn">
                                    <i class="fa-solid fa-user-check"></i> Register Student
                                </button>
                            </form>
                        </div>
                    </div>

                    <div class="grid-column">
                        <div class="card">
                            <div class="card-header">
                                <h2><i class="fa-solid fa-network-wired"></i> Scanning Readers</h2>
                            </div>
                            <div class="card-body no-padding">
                                <div id="device-list-container" class="device-list"></div>
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-header">
                                <h2><i class="fa-solid fa-gauge-high"></i> Hardware Telemetry</h2>
                            </div>
                            <div class="card-body">
                                <div class="telemetry-grid">
                                    <div class="telemetry-item">
                                        <span class="tel-label">Latency</span>
                                        <h4 class="tel-val">42ms</h4>
                                    </div>
                                    <div class="telemetry-item">
                                        <span class="tel-label">Uptime</span>
                                        <h4 class="tel-val text-success">99.9%</h4>
                                    </div>
                                    <div class="telemetry-item">
                                        <span class="tel-label">Packet Loss</span>
                                        <h4 class="tel-val">0.02%</h4>
                                    </div>
                                    <div class="telemetry-item">
                                        <span class="tel-label">Daily Scans</span>
                                        <h4 class="tel-val" id="telemetry-total-writes">10</h4>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
"""

update_html('/Users/nupurbhoir/.gemini/antigravity/scratch/attend_smart/dashboard.html', 'Overview Dashboard', 'Monitor live attendance across campus', 'dashboard', dashboard_main)
update_html('/Users/nupurbhoir/.gemini/antigravity/scratch/attend_smart/simulator.html', 'Check-In Terminal', 'Simulate student badge scans and biometrics', 'simulator', simulator_main)
update_html('/Users/nupurbhoir/.gemini/antigravity/scratch/attend_smart/devices.html', 'Hardware & Onboarding', 'Manage edge devices and register new students', 'devices', devices_main)
print("HTML Refactored!")
