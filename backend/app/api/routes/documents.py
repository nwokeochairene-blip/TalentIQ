import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.document import DocumentExtractionResponse
from app.services.document_service import (
    SUPPORTED_EXTENSIONS,
    DocumentProcessingError,
    extract_text,
    normalize_extracted_text,
)


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)


@router.post(
    "/extract",
    response_model=DocumentExtractionResponse,
)
async def extract_document(
    file: UploadFile = File(...),
) -> DocumentExtractionResponse:
    """Extract text from a PDF or DOCX resume/document."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {extension}. "
                f"Supported types: {sorted(SUPPORTED_EXTENSIONS)}"
            ),
        )

    temp_path = None

    try:
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        temp_file = NamedTemporaryFile(
            suffix=extension,
            delete=False,
        )
        temp_path = temp_file.name

        try:
            temp_file.write(content)
        finally:
            temp_file.close()

        extracted_text = extract_text(temp_path)
        normalized_text = normalize_extracted_text(extracted_text)

        return DocumentExtractionResponse(
            filename=file.filename,
            file_type=extension.lstrip("."),
            character_count=len(normalized_text),
            word_count=len(normalized_text.split()),
            extracted_text=normalized_text,
        )

    except HTTPException:
        raise

    except DocumentProcessingError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Document extraction failed.",
        ) from exc

    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)