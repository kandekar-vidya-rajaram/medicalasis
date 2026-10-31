import os
import time
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from tqdm.auto import tqdm

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("Gemini_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "medicalindex")
UPLOAD_DIR = "./uploaded_docs"

if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

os.makedirs(UPLOAD_DIR, exist_ok=True)


def _get_pinecone_index():
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if not pinecone_api_key:
        raise ValueError("Missing required environment variable: PINECONE_API_KEY")

    pc = Pinecone(api_key=pinecone_api_key)
    spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)
    existing_indexes = [index["name"] for index in pc.list_indexes()]

    if PINECONE_INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=768,
            metric="dotproduct",
            spec=spec,
        )
        while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
            time.sleep(1)

    return pc.Index(PINECONE_INDEX_NAME)


def load_vectorstore(uploaded_files):
    if not uploaded_files:
        raise ValueError("No PDF files were uploaded.")

    if not GOOGLE_API_KEY:
        raise ValueError("Missing required environment variable: GOOGLE_API_KEY or Gemini_API_KEY")

    embed_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    output_dimensionality=768
)
    index = _get_pinecone_index()
    file_paths = []

    for upload in uploaded_files:
        filename = (upload.filename or "uploaded.pdf").strip()
        if not filename.lower().endswith(".pdf"):
            raise ValueError(f"Unsupported file type: {filename}. Only PDF files are allowed.")

        save_path = Path(UPLOAD_DIR) / filename
        with open(save_path, "wb") as file_handle:
            file_handle.write(upload.file.read())
        file_paths.append(str(save_path))

    if not file_paths:
        raise ValueError("No valid PDF files were uploaded.")

    for file_path in file_paths:
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)

        texts = [chunk.page_content for chunk in chunks]
        metadatas = [{**chunk.metadata, "text": chunk.page_content} for chunk in chunks]
        ids = [f"{Path(file_path).stem}-{i}" for i in range(len(chunks))]

        print(f"🔍 Embedding {len(texts)} chunks...")
        embeddings = embed_model.embed_documents(texts)

        print("📤 Uploading to Pinecone...")
        with tqdm(total=len(embeddings), desc="Upserting to Pinecone") as progress:
            index.upsert(vectors=list(zip(ids, embeddings, metadatas)))
            progress.update(len(embeddings))

        print(f"✅ Upload complete for {file_path}")