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
`http://localhost:8501`). Upload PDF documents, then ask a question in the
chat. The backend searches Pinecone for relevant document text and sends that
context with the question to the Groq LLM (`openai/gpt-oss-120b`) to generate
a response. The API returns the generated answer and source filenames, and
Streamlit displays them in the chat. The backend terminal is for server logs,
not the user interface.