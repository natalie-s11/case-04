from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr, validator

class SurveySubmission(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=13, le=120)
    consent: bool = Field(..., description="Must be true to accept")
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=1000)
    user_agent: Optional[str] = None  # NEW: optional field
    submission_id: Optional[str] = None  # NEW: optional field

    @validator("comments")
    def _strip_comments(cls, v):
        return v.strip() if isinstance(v, str) else v

    @validator("consent")
    def _must_consent(cls, v):
        if v is not True:
            raise ValueError("consent must be true")
        return v

class StoredSurveyRecord(SurveySubmission):
    received_at: datetime
    ip: str
    name: str
    consent: bool
    rating: int
    comments: Optional[str] = None
    source: Literal["homepage", "email", "gr", "other"] = "other"
    user_agent: Optional[str] = None

    email: str
    age: str
    submission_id: str


