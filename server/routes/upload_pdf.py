from typing import List

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from server.logger import logger
from server.module.load_vectorstore import load_vectorstore

router = APIRouter()


@router.post("/upload_pdfs/")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    try:
        logger.info("Received uploaded files")
        if not files:
            return JSONResponse(status_code=400, content={"error": "No files were uploaded."})

        await run_in_threadpool(load_vectorstore, files)
        logger.info("Document added to vectorstore")
        return {"messages": "Files processed and vectorstore updated"}
    except Exception as e:
        logger.exception("Error during PDF upload")
        return JSONResponse(status_code=500, content={"error": str(e)})