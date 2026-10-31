# Medical Assistant

The project has two separate processes: a FastAPI backend and a Streamlit
frontend. Start each in its own PowerShell terminal from the project root.

Backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn server.main:app --reload
```

Frontend:

```powershell
.\.venv\Scripts\python.exe -m streamlit run client\utils\app.py
```

Open the Streamlit URL shown in the frontend terminal (normally
`http://localhost:8501`). Ask a question in the chat; the backend returns the
retrieved PDF text as JSON and Streamlit displays it in the chat. The backend
terminal is for server logs, not the user interface.