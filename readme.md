
# Pharmacheck System

This is a web application built with **Flask** for the backend and the frontend.

## Prerequisites

Before setting up the project, make sure you have the following installed:

* **Python 3.x**: Make sure Python is installed. [Download Python](https://www.python.org/downloads/)
* **Visual Studio Code**: Recommended for editing the code. [Download VS Code](https://code.visualstudio.com/)

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
   cd webapp
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


### Step 4: Running the server

In the terminal (make sure your virtual environment is activated), go to the **backend** folder and start the Flask server:

```bash
cd webapp
python app.py
```

By default, Flask will run on `http://127.0.0.1:5000/`. You can now access your backend from the frontend.

---

### Step 5: Testing the Full Application

1. Open your browser and go to the URL served by **Flask** (typically `http://127.0.0.1:5500`).
2. Ensure that the **Flask server** is running at `http://127.0.0.1:5000/` so that the frontend can communicate with it.
3. Interact with the application on the frontend and check the browser's developer console for logs. If everything is set up correctly, the frontend should be able to communicate with the backend via **Socket.IO**.

---

## Project Structure

Here’s a quick overview of the project folder structure:

```
Pharmacheck Website/
│
├── webapp/
│   ├── venv/                      # Python virtual environment
│   ├── .env                       # Environment variables (e.g., Supabase credentials)
│   ├── app.py                      # Flask application
    ├── static/                    # css and js
    ├── templates/                  # html
│   ├── requirements.txt           # Backend dependencies
│
```

---

## Troubleshooting

If you run into any issues, here are a few things to check:

* Ensure your **Flask server** is running on `http://127.0.0.1:5000` 
* If you encounter errors with dependencies, make sure your virtual environment is activated and that you've installed the requirements using `pip install -r requirements.txt`.

---


