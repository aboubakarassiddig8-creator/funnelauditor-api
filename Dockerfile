# ===========================================================
# Image officielle Playwright Python - Chrome + deps inclus
# ===========================================================
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Repertoire de travail
WORKDIR /app

# Variables d'environnement
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Copier et installer les dependances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Verifier que Chromium est disponible
RUN playwright install chromium

# Copier le code source
COPY . .

# Exposer le port par defaut
EXPOSE 8000

# Demarrage via shell form pour que $PORT soit interprete
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
