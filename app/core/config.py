import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key")
    FREE_AUDITS_PER_MONTH: int = 3

    # Google PageSpeed
    GOOGLE_PAGESPEED_KEY: str = os.getenv("GOOGLE_PAGESPEED_KEY", "")

    # Lemon Squeezy
    LEMONSQUEEZY_CHECKOUT_URL: str = os.getenv("LEMONSQUEEZY_CHECKOUT_URL", "")
    LEMONSQUEEZY_WEBHOOK_SECRET: str = os.getenv("LEMONSQUEEZY_WEBHOOK_SECRET", "")

    class Config:
        env_file = ".env"


settings = Settings()
