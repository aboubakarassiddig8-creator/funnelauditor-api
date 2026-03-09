import os
import uuid
import hmac
import hashlib
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from app.services.scraper import scrape_funnel
from app.services.scorer import score_funnel
from app.services.audit import generate_audit
from app.core.config import settings

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
        # Check free audit limit
        user_response = supabase.table("profiles").select("is_pro, audits_count").eq("id", request.user_id).single().execute()
        profile = user_response.data
        if not profile.get("is_pro", False) and profile.get("audits_count", 0) >= settings.FREE_AUDITS_PER_MONTH:
            raise HTTPException(status_code=403, detail="Free audit limit reached. Please upgrade to Pro.")

        audit_id = str(uuid.uuid4())
        scraped = await scrape_funnel(request.url)
        scores = score_funnel(scraped)
        audit_report = generate_audit(scraped, scores)

        # Google PageSpeed
        pagespeed_score = None
        if settings.GOOGLE_PAGESPEED_KEY:
            try:
                async with httpx.AsyncClient() as client:
                    ps_resp = await client.get(
                        "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
                        params={"url": request.url, "key": settings.GOOGLE_PAGESPEED_KEY, "strategy": "mobile"},
                        timeout=30.0
                    )
                    ps_data = ps_resp.json()
                    pagespeed_score = int(ps_data["lighthouseResult"]["categories"]["performance"]["score"] * 100)
            except Exception:
                pagespeed_score = None

        data = {
            "id": audit_id,
            "user_id": request.user_id,
            "url": request.url,
            "score": scores["global"],
            "report": audit_report,
            "screenshot_url": scraped.get("screenshot_url", ""),
            "status": "completed",
            "pagespeed_score": pagespeed_score,
        }
        supabase.table("audits").insert(data).execute()

        # Increment audits_count
        supabase.table("profiles").update({"audits_count": profile.get("audits_count", 0) + 1}).eq("id", request.user_id).execute()

        return {"audit_id": audit_id, "score": scores["global"], "report": audit_report, "pagespeed_score": pagespeed_score}
    except HTTPException:
        raise
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


@app.get("/upgrade")
def get_upgrade_url():
    return {"checkout_url": settings.LEMONSQUEEZY_CHECKOUT_URL}


@app.post("/webhook/lemonsqueezy")
async def lemonsqueezy_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Signature", "")
    secret = settings.LEMONSQUEEZY_WEBHOOK_SECRET.encode()
    expected = hmac.new(secret, body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()
    event = payload.get("meta", {}).get("event_name", "")

    if event == "order_created":
        custom_data = payload.get("meta", {}).get("custom_data", {})
        user_id = custom_data.get("user_id")
        if user_id:
            supabase.table("profiles").update({"is_pro": True, "audits_count": 0}).eq("id", user_id).execute()

    return {"status": "ok"}
