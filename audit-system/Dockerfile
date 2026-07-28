# Système d'audit DaatTorah — API (Phase 1, audit_readonly)
FROM python:3.12-slim

WORKDIR /app

# lxml a besoin des bibliothèques système au build sur certaines plateformes ;
# les wheels binaires suffisent en général, on reste minimal.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV AUDIT_MODE=audit_readonly
EXPOSE 8000

# Les migrations sont appliquées au démarrage, puis l'API démarre.
CMD ["sh", "-c", "alembic upgrade head && uvicorn daat_audit.api.main:app --host 0.0.0.0 --port 8000"]
