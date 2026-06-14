css_content = """/* Modern Clean Dashboard Styles - AttendSmart */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --sidebar-width: 260px;
    --bg-app: #f3f6f9;
    --bg-sidebar: #ffffff;
    --bg-card: #ffffff;
    
    --primary: #ff7a00;
    --primary-hover: #ea580c;
    --accent: #3b82f6;
    --accent-hover: #2563eb;
    
    --text-dark: #111827;
    --text-gray: #6b7280;
    --text-light: #ffffff;
    
    --border-color: #e5e7eb;
    --border-radius-lg: 16px;
    --border-radius-md: 10px;
    --border-radius-sm: 6px;
    
    --shadow-soft: 0 4px 20px rgba(0, 0, 0, 0.03);
    --shadow-hover: 0 10px 25px rgba(0, 0, 0, 0.06);
    
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Outfit', sans-serif;
    background-color: var(--bg-app);
    color: var(--text-dark);
    -webkit-font-smoothing: antialiased;
}

/* Scrollbars */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #9ca3af; }

/* Animations */
@keyframes slideUp {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
.slide-up-animation { animation: slideUp 0.4s ease-out forwards; }

.mt-3 { margin-top: 1rem; }
.mt-4 { margin-top: 1.5rem; }

/* APP LAYOUT */
.app-layout {
    display: flex;
    min-height: 100vh;
    width: 100%;
}

/* SIDEBAR */
.sidebar {
    width: var(--sidebar-width);
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    padding: 1.5rem 0;
    position: fixed;
    height: 100vh;
    z-index: 100;
}

.sidebar-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0 1.5rem 2rem 1.5rem;
}

.logo-icon {
    width: 36px; height: 36px;
    border-radius: 8px;
    background: var(--primary);
    color: white;
    display: flex; justify-content: center; align-items: center;
    font-size: 1.1rem;
    box-shadow: 0 4px 12px rgba(255, 122, 0, 0.3);
}

.logo-text h1 {
    font-size: 1.35rem; font-weight: 800; letter-spacing: -0.5px;
}

.sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 0 1rem;
    flex: 1;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.85rem 1rem;
    border-radius: var(--border-radius-md);
    text-decoration: none;
    color: var(--text-gray);
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.2s;
}

.nav-item i { font-size: 1.1rem; width: 20px; text-align: center; }

.nav-item:hover {
    background: #f3f4f6;
    color: var(--text-dark);
}

.nav-item.active {
    background: rgba(255, 122, 0, 0.08);
    color: var(--primary);
}

.sidebar-footer {
    padding: 1rem;
    border-top: 1px solid var(--border-color);
}

.nav-btn-logout {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.85rem 1rem;
    border-radius: var(--border-radius-md);
    background: none; border: none;
    color: var(--danger);
    font-weight: 600; font-size: 0.95rem; font-family: 'Outfit';
    cursor: pointer; transition: all 0.2s;
}
.nav-btn-logout:hover { background: #fee2e2; }

/* MAIN CONTENT */
.main-wrapper {
    flex: 1;
    margin-left: var(--sidebar-width);
    display: flex;
    flex-direction: column;
}

.top-header {
    padding: 1.5rem 2.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-title h2 { font-size: 1.8rem; font-weight: 800; color: var(--text-dark); }
.header-title p { font-size: 0.9rem; color: var(--text-gray); margin-top: 0.2rem; }

.header-status { display: flex; gap: 1rem; align-items: center; }

.status-pill, .clock-area {
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem; font-weight: 700;
    display: flex; align-items: center; gap: 0.5rem;
    background: white;
    border: 1px solid var(--border-color);
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.status-pill.online { color: var(--success); }
.status-pill.offline { color: var(--danger); }
.status-pill.pending { color: var(--warning); }
.clock-area { color: var(--text-gray); }

.status-dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; }

.page-content {
    padding: 0 2.5rem 2.5rem 2.5rem;
    flex: 1;
}

/* CARDS */
.card {
    background: var(--bg-card);
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow-soft);
    border: 1px solid rgba(229, 231, 235, 0.5);
    display: flex; flex-direction: column;
    overflow: hidden;
}

.card-header {
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid var(--border-color);
    display: flex; justify-content: space-between; align-items: center;
    background: #ffffff;
}

.card-header h2 { font-size: 1.1rem; font-weight: 700; color: var(--text-dark); display: flex; align-items: center; gap: 0.5rem; }
.card-header h2 i { color: var(--primary); }

.card-body { padding: 1.5rem; }
.card-body.no-padding { padding: 0; }
.card-desc { font-size: 0.85rem; color: var(--text-gray); margin-bottom: 1.25rem; }

/* METRICS */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
}

.metric-card {
    border-radius: var(--border-radius-lg);
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.25rem;
    color: white;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-3px); }

.metric-gradient-green { background: linear-gradient(135deg, #10b981, #059669); }
.metric-gradient-orange { background: linear-gradient(135deg, #f59e0b, #d97706); }
.metric-gradient-red { background: linear-gradient(135deg, #ef4444, #dc2626); }
.metric-gradient-blue { background: linear-gradient(135deg, #3b82f6, #2563eb); }

.metric-icon {
    width: 48px; height: 48px; border-radius: 12px; background: rgba(255,255,255,0.2);
    display: flex; justify-content: center; align-items: center; font-size: 1.4rem;
}

.metric-label { font-size: 0.85rem; font-weight: 600; opacity: 0.9; }
.metric-info h3 { font-size: 1.75rem; font-weight: 800; margin-top: 0.2rem; }

/* LAYOUT GRIDS */
.dashboard-analytics-layout {
    display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem;
}
.devices-layout-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;
}
.simulator-layout-grid { display: flex; justify-content: center; }
.simulator-terminal-card { width: 100%; max-width: 800px; }
.grid-column { display: flex; flex-direction: column; gap: 1.5rem; }

/* ROSTER TABLE */
.table-responsive { overflow-x: auto; }
.roster-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.roster-table th { background: #f9fafb; padding: 1rem 1.5rem; font-weight: 600; color: var(--text-gray); text-align: left; border-bottom: 1px solid var(--border-color); }
.roster-table td { padding: 1rem 1.5rem; border-bottom: 1px solid var(--border-color); color: var(--text-dark); vertical-align: middle; }
.roster-table tr:hover td { background: #f9fafb; }
.roster-table code { font-family: 'JetBrains Mono'; background: #f3f4f6; padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.8rem; color: var(--text-dark); }

.avatar {
    width: 36px; height: 36px; border-radius: 50%; color: white; display: inline-flex; justify-content: center; align-items: center; font-weight: 700; font-size: 0.85rem;
}
.av-indigo { background: #4f46e5; }
.av-orange { background: #ff7a00; }
.av-teal { background: #0d9488; }
.av-rose { background: #ec4899; }
.av-blue { background: #2563eb; }

.student-name-cell { display: flex; align-items: center; gap: 0.75rem; }
.s-name { font-weight: 600; }

.pill-badge { padding: 0.3rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.status-good { background: #d1fae5; color: #047857; }
.status-warning { background: #fef3c7; color: #b45309; }
.status-danger { background: #fee2e2; color: #b91c1c; }

/* ACTIVITY FEED */
.activity-feed { max-height: 300px; overflow-y: auto; }
.notification-list { max-height: 250px; overflow-y: auto; }
.activity-item, .notif-item { padding: 1rem 1.5rem; border-bottom: 1px solid var(--border-color); display: flex; gap: 1rem; }
.activity-item:hover, .notif-item:hover { background: #f9fafb; }

.activity-icon-container {
    width: 36px; height: 36px; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 0.9rem; flex-shrink: 0;
}
.success-type .activity-icon-container { background: #d1fae5; color: #059669; }
.late-type .activity-icon-container { background: #fef3c7; color: #d97706; }
.error-type .activity-icon-container { background: #fee2e2; color: #dc2626; }
.system-type .activity-icon-container { background: #f3f4f6; color: #4b5563; }
.kafka-type .activity-icon-container { background: #dbeafe; color: #2563eb; }

.activity-content p, .notif-text { font-size: 0.85rem; color: var(--text-dark); margin-top: 0.2rem; }
.activity-time, .notif-time { font-size: 0.7rem; font-weight: 700; color: var(--text-gray); }

/* FORMS */
.form-group { margin-bottom: 1.25rem; }
.form-group label { display: block; font-size: 0.85rem; font-weight: 600; color: var(--text-dark); margin-bottom: 0.5rem; }

.form-control {
    width: 100%;
    background-color: #f9fafb !important;
    border: 1px solid #d1d5db;
    border-radius: var(--border-radius-md);
    padding: 0.75rem 1rem;
    color: var(--text-dark) !important;
    font-family: 'Outfit'; font-size: 0.95rem; font-weight: 500;
    transition: all 0.2s;
    outline: none;
}
.form-control:focus { border-color: var(--primary); background-color: #ffffff !important; box-shadow: 0 0 0 3px rgba(255, 122, 0, 0.1); }
.form-control::placeholder { color: #9ca3af; font-weight: 400; }

input:-webkit-autofill { -webkit-box-shadow: 0 0 0 50px #f9fafb inset !important; -webkit-text-fill-color: var(--text-dark) !important; }

/* Preset buttons & sliders */
.label-with-presets { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.label-with-presets label { margin-bottom: 0; }
.preset-links { display: flex; gap: 0.5rem; }
.preset-btn { background: #f3f4f6; border: none; border-radius: 4px; padding: 0.2rem 0.5rem; font-size: 0.75rem; font-weight: 600; color: var(--text-gray); cursor: pointer; }
.preset-btn:hover { background: var(--primary); color: white; }
.preset-btn.warning-preset:hover { background: var(--accent); }
.preset-btn.error-preset:hover { background: var(--danger); }

.coordinate-inputs { display: flex; gap: 0.75rem; }

.slider-container { display: flex; align-items: center; gap: 1rem; }
.form-range { flex: 1; accent-color: var(--primary); }
.slider-badge { background: #f3f4f6; padding: 0.4rem 0.8rem; border-radius: 6px; font-weight: 700; font-size: 0.85rem; }

/* Time Window Simulation (Grid of big buttons) */
.timestamp-presets { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }
.time-btn {
    background: #f9fafb; border: 1px solid var(--border-color); border-radius: var(--border-radius-md);
    padding: 1rem; display: flex; flex-direction: column; align-items: center; gap: 0.25rem;
    cursor: pointer; transition: all 0.2s;
}
.time-btn-title { font-weight: 700; font-size: 0.9rem; color: var(--text-dark); }
.time-btn-sub { font-size: 0.75rem; color: var(--text-gray); }
.time-btn:hover { border-color: var(--primary); background: #fffaf5; }
.time-btn.active { border-color: var(--primary); background: #fffaf5; box-shadow: 0 0 0 2px var(--primary); }
.time-btn.active .time-btn-title { color: var(--primary); }

.simulator-form-flex { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }

/* BUTTONS */
.btn {
    font-family: 'Outfit'; font-weight: 700; font-size: 0.95rem;
    padding: 0.75rem 1.5rem; border-radius: var(--border-radius-md);
    border: none; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 0.5rem;
    transition: all 0.2s;
}
.btn-primary { background: var(--primary); color: white; }
.btn-primary:hover { background: var(--primary-hover); transform: translateY(-1px); }
.btn-secondary { background: #f3f4f6; color: var(--text-dark); border: 1px solid var(--border-color); }
.btn-secondary:hover { background: #e5e7eb; }
.btn-block { width: 100%; }
.btn-lg { padding: 1rem; font-size: 1.05rem; }
.shadow-btn { box-shadow: 0 4px 12px rgba(255, 122, 0, 0.2); }

.btn-clear { background: none; border: none; color: var(--text-gray); cursor: pointer; font-size: 1.1rem; }
.btn-clear:hover { color: var(--danger); }

/* ALERTS */
.alert-box {
    padding: 1rem; border-radius: var(--border-radius-md); font-weight: 600; font-size: 0.9rem;
    display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;
}
.alert-box.success { background: #d1fae5; color: #065f46; border: 1px solid #34d399; }
.alert-box.hidden { display: none !important; }

/* DEVICE REGISTRY */
.device-row { display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border-color); }
.device-row:last-child { border-bottom: none; }
.dev-name { font-weight: 700; font-size: 1rem; color: var(--text-dark); }
.dev-id { font-family: 'JetBrains Mono'; font-size: 0.8rem; color: var(--text-gray); }

/* SWITCH */
.switch { position: relative; display: inline-block; width: 48px; height: 26px; }
.switch input { opacity: 0; width: 0; height: 0; }
.switch-slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #d1d5db; transition: .3s; border-radius: 34px; }
.switch-slider:before { position: absolute; content: ""; height: 20px; width: 20px; left: 3px; bottom: 3px; background-color: white; transition: .3s; border-radius: 50%; }
input:checked + .switch-slider { background-color: var(--success); }
input:checked + .switch-slider:before { transform: translateX(22px); }

/* TELEMETRY */
.telemetry-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.telemetry-item { background: #f9fafb; border: 1px solid var(--border-color); border-radius: var(--border-radius-md); padding: 1.25rem; }
.tel-label { font-size: 0.75rem; font-weight: 700; color: var(--text-gray); text-transform: uppercase; }
.tel-val { font-size: 1.5rem; font-weight: 800; margin-top: 0.5rem; color: var(--text-dark); }
.text-success { color: var(--success); }

/* RESPONSIVE */
@media (max-width: 1024px) {
    .dashboard-analytics-layout { grid-template-columns: 1fr; }
    .devices-layout-grid { grid-template-columns: 1fr; }
    .metrics-grid { grid-template-columns: repeat(2, 1fr); }
    .simulator-form-flex { grid-template-columns: 1fr; gap: 1rem; }
}

@media (max-width: 768px) {
    .sidebar { width: 80px; }
    .logo-text, .nav-item span { display: none; }
    .main-wrapper { margin-left: 80px; }
    .metrics-grid { grid-template-columns: 1fr; }
}
"""

with open('/Users/nupurbhoir/.gemini/antigravity/scratch/attend_smart/style.css', 'w') as f:
    f.write(css_content)
