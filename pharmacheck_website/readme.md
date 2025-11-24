
# Pharmacheck System

This is a web application built with **Flask** for the backend and **HTML/CSS/JavaScript** for the frontend. The frontend is served via Live Server in a development environment. The backend provides an API, while the frontend communicates with it through **Socket.IO**.

## Prerequisites

Before setting up the project, make sure you have the following installed:

* **Python 3.x**: Make sure Python is installed. [Download Python](https://www.python.org/downloads/)
* **Node.js and npm**: Required for Live Server (if you don't have it). [Download Node.js](https://nodejs.org/)
* **Visual Studio Code**: Recommended for editing the code and using Live Server. [Download VS Code](https://code.visualstudio.com/)

---

## Setup Instructions

### Step 1: Clone the Repository

First, clone this repository to your local machine (or download the project if you haven't done that yet).

```bash
git clone https://github.com/nataliexsalome/PharmaCheck.git
cd pharmacheck-website
```

### Step 2: Set Up the Virtual Environment

1. Open **Command Prompt** and navigate to your project directory:

   ```cmd
   cd backend
   ```

2. **Create a virtual environment**:

   ```cmd
   python -m venv venv
   ```

3. **Activate the virtual environment**:

   * **For Command Prompt:**

     ```cmd
     venv\Scripts\activate
     ```

   * **For PowerShell:**

     ```powershell
     .\venv\Scripts\Activate
     ```

   You should see `(venv)` appear in your command prompt, indicating that the virtual environment is activated.

---

### Step 3: Install Backend Dependencies

With the virtual environment activated, **install the required Python packages**:

```bash
pip install -r requirements.txt
```

This will install all the required libraries for the Flask backend, including `flask`, `flask-socketio`, `supabase`, and others.

---

### Step 4: Set Up the Frontend

1. **Open the `index.html` file** in Visual Studio Code (VS Code).

2. **Install Live Server Extension** in VS Code if you haven't already:

   * Go to Extensions (`Ctrl+Shift+X`) and search for **Live Server**.
   * Install it.

3. **Launch the frontend with Live Server**:

   * Right-click on `index.html` and select **Open with Live Server**.
   * This will open the frontend in your browser at `http://127.0.0.1:5500`.

---

### Step 5: Running the Backend

In the terminal (make sure your virtual environment is activated), go to the **backend** folder and start the Flask server:

```bash
cd backend
python app.py
```

By default, Flask will run on `http://127.0.0.1:5000/`. You can now access your backend from the frontend.

---

### Step 6: Testing the Full Application

1. Open your browser and go to the URL served by **Live Server** (typically `http://127.0.0.1:5500`).
2. Ensure that the **Flask server** is running at `http://127.0.0.1:5000/` so that the frontend can communicate with it.
3. Interact with the application on the frontend and check the browser's developer console for logs. If everything is set up correctly, the frontend should be able to communicate with the backend via **Socket.IO**.

---

## Project Structure

Here’s a quick overview of the project folder structure:

```
Pharmacheck Website/
│
├── backend/
│   ├── venv/                      # Python virtual environment
│   ├── .env                       # Environment variables (e.g., Supabase credentials)
│   ├── app.py                     # Flask application
│   ├── requirements.txt           # Backend dependencies
│
├── css/
│   ├── report.css                 # CSS styles for report page
│   ├── verify.css                 # CSS styles for verification page
│
├── js/
│   ├── report.js                  # JavaScript for the report page
│   ├── socket.js                  # Socket.IO communication
│   ├── verify.js                  # JavaScript for the verification page
│   ├── index.html                 # Main HTML file served by Live Server
│   ├── reportcontact.html         # Another HTML file (likely for a contact page)
│
├── images/                        # Folder for image assets
```

---

## Troubleshooting

If you run into any issues, here are a few things to check:

* Ensure your **Flask backend** is running on `http://127.0.0.1:5000` while you are running Live Server on the frontend.
* If the frontend cannot connect to the backend via **Socket.IO**, double-check the connection URL in your JavaScript code (e.g., `io("http://127.0.0.1:5000")`).
* If you encounter errors with dependencies, make sure your virtual environment is activated and that you've installed the requirements using `pip install -r requirements.txt`.

---

## Additional Notes

* The backend is built using **Flask** and **Flask-SocketIO**, allowing real-time communication between the frontend and the backend.
* The frontend is served using **Live Server** in VS Code, allowing you to preview changes instantly during development.

---
