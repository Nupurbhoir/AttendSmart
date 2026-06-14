# AttendSmart: Setup and Troubleshooting Guide

This guide contains everything you need to know to run the AttendSmart project from start to finish inside VS Code, and how to fix common errors you might run into during your presentation.

---

## 🚀 How to Run the Project from Scratch

1. **Open the Project in VS Code**
   - Open VS Code.
   - Go to `File > Open Folder...` and select the `attend_smart` folder (or the extracted `source_code` folder).

2. **Start the Python Backend Server**
   - Open a new terminal in VS Code by clicking `Terminal > New Terminal` at the top.
   - Make sure you are inside the project folder in the terminal.
   - Run this exact command to start the server:
     ```bash
     python3 server.py
     ```
   - *Success Message:* You should see `Starting AttendSmart API Gateway on port 8000...` printed in the terminal. **Do not close this terminal!** Leave it running in the background.

3. **Open the Application in your Browser**
   - Open Google Chrome (or Safari/Edge).
   - Type this exact address into the URL bar and hit Enter:
     ```text
     http://localhost:8000/home.html
     ```
   - From here, you can click "Admin Portal" to see the Dashboard, or "Faculty Portal" to open the Simulator.

---

## 🛑 Common Errors & How to Fix Them

### Error 1: "Address already in use" or "Port 8000 is busy"
**What it means:** You already have a hidden Python server running in the background, and your new server can't start because the old one is blocking the port.
**How to fix it:**
1. Click inside your VS Code terminal.
2. Press **`Control + C`** on your keyboard to kill the running server.
3. Type `python3 server.py` and press Enter to start a fresh server.
*(If that doesn't work, completely close VS Code, open it again, and try starting the server).*

### Error 2: "This site can't be reached" (localhost refused to connect)
**What it means:** Your browser is trying to load the page, but your Python server is turned off or crashed.
**How to fix it:**
1. Go back to your VS Code terminal.
2. Run `python3 server.py`.
3. Go back to your browser and click the **Refresh** button.

### Error 3: The database isn't updating / The UI is showing old data
**What it means:** Sometimes your browser "caches" (saves) an old version of your JavaScript or HTML files, so it doesn't load the newest code you wrote.
**How to fix it:**
1. Do a **Hard Refresh** in your browser. 
   - On Mac: Press `Command + Shift + R`
   - On Windows: Press `Control + Shift + R`
2. If the Python logic seems wrong, click your terminal, press `Control + C`, and restart `python3 server.py`.

### Error 4: "BIOMETRIC_CONFIDENCE_LOW" or old simulator text is showing
**What it means:** You are accidentally running an old version of the `server.py` file.
**How to fix it:**
1. Kill the server in the terminal (`Control + C`).
2. Make sure you are in the correct, most recent `attend_smart` folder.
3. Start the server again (`python3 server.py`).

---

## 🎯 Pro-Tips for your Panel Presentation

* **Always start fresh:** Before you share your screen with the panel, kill your terminal (`Control + C`) and start `python3 server.py` so you know it's a completely fresh run.
* **Keep two tabs open:** Open `localhost:8000/dashboard.html` in one browser tab, and `localhost:8000/simulator.html` in another tab side-by-side. This lets you quickly show the panel how a check-in on the simulator instantly updates the dashboard numbers!
* **Show the Kafka code:** If they ask about backend scale, open `kafka_producer.py` in your VS Code editor to show them the production Kafka implementation.
