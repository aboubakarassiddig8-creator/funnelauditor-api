import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from app.services.scraper import scrape_funnel
from app.services.scorer import score_funnel
from app.services.audit import generate_audit

app = FastAPI(title="FunnelAuditor API")

# Origines explicitement autorisees (Lovable preview + production)
ALLOWED_ORIGINS = [
    "https://lovable.app",
    "https://www.lovable.app",
    "https://funnelauditor.lovable.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://(id-preview--[a-zA-Z0-9-]+\.lovable\.app|[a-zA-Z0-9-]+\.lovable\.app)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


class AuditRequest(BaseModel):
    url: str
    user_id: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/audit")
async def create_audit(request: AuditRequest):
    try:
        audit_id = str(uuid.uuid4())
        scraped = await scrape_funnel(request.url)
        scores = score_funnel(scraped)
        audit_report = generate_audit(scraped, scores)
        data = {
            "id": audit_id,
            "user_id": request.user_id,
            "url": request.url,
            "score": scores["global"],
            "report": audit_report,
            "screenshot_url": scraped.get("screenshot_url", ""),
            "status": "completed",
        }
        supabase.table("audits").insert(data).execute()
        return {"audit_id": audit_id, "score": scores["global"], "report": audit_report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audits/{user_id}")
def get_user_audits(user_id: str):
    try:
        response = supabase.table("audits").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return {"audits": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audit/{audit_id}")
def get_audit(audit_id: str):
    try:
        response = supabase.table("audits").select("*").eq("id", audit_id).single().execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
