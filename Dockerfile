# ============================================================
# Image officielle Playwright Python — Chrome + deps inclus
# ============================================================
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Repertoire de travail
WORKDIR /app

# Variables d'environnement Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copier les dependances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# S'assurer que Chromium est bien installe (securite)
RUN playwright install chromium

# Copier tout le code source
COPY . .

# Exposer le port (Railway injecte $PORT au runtime)
EXPOSE 8000

# Commande de demarrage
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
