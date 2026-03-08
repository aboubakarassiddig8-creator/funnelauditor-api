import os
import base64
from playwright.async_api import async_playwright
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


async def scrape_funnel(url: str) -> dict:
    result = {
        "url": url,
        "title": "",
        "headline": "",
        "cta_text": "",
        "cta_count": 0,
        "has_video": False,
        "has_testimonials": False,
        "has_form": False,
        "form_fields": 0,
        "load_time": 0,
        "screenshot_url": "",
        "html_content": "",
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = await browser.new_page()

        import time
        start = time.time()
        await page.goto(url, wait_until="networkidle", timeout=30000)
        result["load_time"] = round(time.time() - start, 2)

        result["title"] = await page.title()
        result["html_content"] = await page.content()

        # Screenshot
        screenshot_bytes = await page.screenshot(full_page=True)
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode()

        # Upload to Supabase
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
            filename = f"screenshots/{url.replace('https://', '').replace('/', '_')}.png"
            supabase.storage.from_("audits").upload(
                filename,
                screenshot_bytes,
                {"content-type": "image/png"}
            )
            result["screenshot_url"] = f"{SUPABASE_URL}/storage/v1/object/public/audits/{filename}"
        except Exception:
            pass

        # Extract headline
        h1 = await page.query_selector("h1")
        if h1:
            result["headline"] = await h1.inner_text()

        # CTAs
        ctas = await page.query_selector_all("a[href], button")
        result["cta_count"] = len(ctas)
        if ctas:
            result["cta_text"] = await ctas[0].inner_text()

        # Video
        video = await page.query_selector("video, iframe[src*='youtube'], iframe[src*='vimeo']")
        result["has_video"] = video is not None

        # Form
        form = await page.query_selector("form")
        result["has_form"] = form is not None
        if form:
            inputs = await page.query_selector_all("input:not([type='hidden']), textarea")
            result["form_fields"] = len(inputs)

        # Testimonials
        content = result["html_content"].lower()
        result["has_testimonials"] = any(word in content for word in ["testimonial", "review", "avis", "temoignage", "client"])

        await browser.close()

    return result
