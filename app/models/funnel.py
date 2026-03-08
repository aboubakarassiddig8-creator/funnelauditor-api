from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AuditRequest(BaseModel):
    url: str
    user_id: str


class AuditScore(BaseModel):
    headline: int = 0
    cta: int = 0
    video: int = 0
    testimonials: int = 0
    form: int = 0
    speed: int = 0
    global_score: int = 0


class AuditReport(BaseModel):
    strengths: List[str] = []
    recommendations: List[str] = []
    global_score: int = 0
    grade: str = "F"


class AuditRecord(BaseModel):
    id: str
    user_id: str
    url: str
    score: int
    report: dict
    screenshot_url: Optional[str] = ""
    status: str = "completed"
    created_at: Optional[datetime] = None


class AuditResponse(BaseModel):
    audit_id: str
    score: int
    report: dict
