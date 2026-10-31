import requests

from client.utils.config import API_URL


def ask_question(question):
    return requests.post(
        f"{API_URL}/ask/",
        data={"question": question},
        timeout=(10, 180),
    )


def upload_pdfs_api(uploaded_files):
    files = [
        ("files", (file.name, file.getvalue(), file.type or "application/pdf"))
        for file in uploaded_files
    ]
    return requests.post(
        f"{API_URL}/upload_pdfs/",
        files=files,
        timeout=(10, 300),
    )
