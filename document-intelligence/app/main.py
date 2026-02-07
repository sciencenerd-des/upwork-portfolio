"""FastAPI application for document intelligence processing."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.config import get_settings
from app.models import ProcessResponse, QARequest, QAResponse
from src.exporter import export_csv, export_excel, export_json
from src.pipeline import ProcessedDocument, run_pipeline
from src.qa_engine import answer_question

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOCUMENT_STORE: dict[str, ProcessedDocument] = {}


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "documents_cached": len(DOCUMENT_STORE),
        "max_upload_mb": settings.max_upload_mb,
    }


@app.post("/process", response_model=ProcessResponse)
async def process_document(file: UploadFile = File(...)) -> ProcessResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing.")

    content = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max allowed size is {settings.max_upload_mb} MB.",
        )

    try:
        result = run_pipeline(content, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}") from exc

    DOCUMENT_STORE[result.document_id] = result
    return ProcessResponse(**result.response_payload())


@app.post("/qa", response_model=QAResponse)
def ask_question(payload: QARequest) -> QAResponse:
    document = DOCUMENT_STORE.get(payload.document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found in current session.")

    qa_result = answer_question(payload.question, document.chunks)
    return QAResponse(
        document_id=payload.document_id,
        question=payload.question,
        answer=str(qa_result["answer"]),
        sources=list(qa_result["sources"]),
        confidence=float(qa_result["confidence"]),
    )


@app.get("/export/{document_id}/{export_format}")
def export_document(document_id: str, export_format: str) -> Response:
    document = DOCUMENT_STORE.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found in current session.")

    safe_name = document.filename.rsplit(".", 1)[0]

    if export_format == "json":
        payload = {
            "document": document.response_payload(),
            "full_text": document.text,
        }
        data = export_json(payload)
        return Response(
            content=data,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="{safe_name}_entities.json"'
            },
        )

    if export_format == "csv":
        data = export_csv(document.entities)
        return Response(
            content=data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{safe_name}_entities.csv"'
            },
        )

    if export_format == "xlsx":
        data = export_excel(
            filename=document.filename,
            summary=document.summary,
            key_points=document.key_points,
            entities=document.entities,
        )
        return Response(
            content=data,
            media_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition": f'attachment; filename="{safe_name}_entities.xlsx"'
            },
        )

    raise HTTPException(status_code=400, detail="Invalid format. Use json, csv, or xlsx.")
