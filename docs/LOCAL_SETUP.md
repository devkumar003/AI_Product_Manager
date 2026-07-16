# AI ProductOS: Local Setup Guide

Follow this guide to install dependencies, configure environment variables, run database migrations, and start both the backend and frontend servers on your local machine.

---

## 📋 Prerequisites
Ensure you have the following installed:
*   **Python** (v3.10 to v3.12)
*   **Node.js** (v18 or higher) & **npm**
*   **Git**
*   **Redis Server** (Optional: local memory fallback is automatically used if Redis is not configured or offline)

---

## 🛠️ Backend Installation & Setup

1.  **Navigate to the backend directory**:
    ```powershell
    cd backend
    ```
2.  **Create a virtual environment**:
    *   *Windows*:
        ```powershell
        python -m venv .venv
        ```
    *   *macOS/Linux*:
        ```bash
        python3 -m venv .venv
        ```
3.  **Activate the virtual environment**:
    *   *Windows PowerShell*:
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
    *   *Windows CMD*:
        ```cmd
        .venv\Scripts\activate.bat
        ```
    *   *macOS/Linux*:
        ```bash
        source .venv/bin/activate
        ```
4.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Configure Environment Variables**:
    Copy the sample configuration file and customize:
    ```bash
    copy .env.example .env
    ```
    *Open `.env` and fill in necessary LLM API keys (e.g. `OPENAI_API_KEY`, `GEMINI_API_KEY`)*.

6.  **Run Database Migrations**:
    ```bash
    alembic upgrade head
    ```

7.  **Start the Backend server**:
    ```bash
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
    ```

---

## 🎨 Frontend Installation & Setup

1.  **Navigate to the frontend directory**:
    ```powershell
    cd ../frontend
    ```
2.  **Install Node packages**:
    ```bash
    npm install
    ```
3.  **Configure Environment Variables**:
    Copy the sample configuration file:
    ```bash
    copy .env.example .env
    ```
    Ensure `NEXT_PUBLIC_API_URL` is set to `http://localhost:8000/api/v1`.

4.  **Start the Frontend development server**:
    ```bash
    npm run dev
    ```
    Open [http://localhost:3000](http://localhost:3000) in your web browser.

---

## 💡 Troubleshooting & Common Errors

### 1. Database Migrations Out of Sync
*   **Error**: `Relation "chat_messages" does not exist` or similar during migrations.
*   **Solution**: Ensure your DB migrations chain is properly applied up to head. Run `alembic upgrade head`. If starting fresh, delete `test.db` and run `alembic upgrade head` to recreate the schema.

### 2. Permission Denied on `uploads/`
*   **Error**: `PermissionError: [Errno 13] Permission denied: 'uploads'` (especially in container environments).
*   **Solution**: Ensure the folder `uploads` is pre-created and has proper read/write permissions for the user executing the app process.
