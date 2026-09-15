from pydantic import BaseModel, Field


class DocumentExtractionResponse(BaseModel):
    filename: str = Field(..., description="Original document filename")
    file_type: str = Field(..., description="Detected document type")
    character_count: int = Field(..., ge=0)
    word_count: int = Field(..., ge=0)
    extracted_text: str
