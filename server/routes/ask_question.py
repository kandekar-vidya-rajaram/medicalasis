
import os

from dotenv import load_dotenv
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone

from server.logger import logger
from server.module.llm import generate_answer

router = APIRouter()
load_dotenv()


@router.post("/ask/")
async def ask_question(question: str = Form(...)):
    try:
        # 1. Validate the question
        if not question or not question.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Question cannot be empty."}
            )

        logger.info(f"User query: {question}")

        # 2. Get API keys and index name
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_index_name = os.getenv(
            "PINECONE_INDEX_NAME", "medicalindex"
        )
        google_api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("Gemini_API_KEY")
        )

        if not pinecone_api_key:
            return JSONResponse(
                status_code=500,
                content={"error": "Missing PINECONE_API_KEY"}
            )

        if not google_api_key:
            return JSONResponse(
                status_code=500,
                content={"error": "Missing Google API key"}
            )

        os.environ["GOOGLE_API_KEY"] = google_api_key

        # 3. Connect to Pinecone
        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index(pinecone_index_name)

        # 4. Convert question into an embedding
        embed_model = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            output_dimensionality=768
        )

        embedded_query = embed_model.embed_query(question)

        # 5. Search Pinecone
        res = index.query(
            vector=embedded_query,
            top_k=5,
            include_metadata=True
        )

        matches = res.get("matches", [])
        logger.info(f"Pinecone match count: {len(matches)}")

        # 6. Collect retrieved text for the frontend response
        docs = []

        for match in matches:
            metadata = match.get("metadata") or {}
            content = metadata.get("text", "")

            if content.strip():
                docs.append(
                    Document(
                        page_content=content,
                        metadata=metadata
                    )
                )

        if not docs:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "No document text was retrieved from Pinecone.",
                    "matches_found": len(matches)
                }
            )

        context = "\n\n".join(doc.page_content for doc in docs)
        answer = generate_answer(question.strip(), context)

        return {
            "response": answer,
            "matches_found": len(docs),
            "sources": [
                doc.metadata.get("source", "") for doc in docs
            ]
        }

    except Exception as e:
        logger.exception("Error processing question")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
