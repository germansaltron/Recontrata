# Stage 1: Build frontend
FROM node:22-alpine AS frontend-build
ARG VITE_CLERK_PUBLISHABLE_KEY
ARG VITE_API_URL=/api/v1
# Observabilidad y feedback del beta (build-time; Railway los inyecta como build args).
ARG VITE_SENTRY_DSN
ARG VITE_SENTRY_ENVIRONMENT=production
ARG VITE_FEEDBACK_URL
ENV VITE_CLERK_PUBLISHABLE_KEY=$VITE_CLERK_PUBLISHABLE_KEY
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_SENTRY_DSN=$VITE_SENTRY_DSN
ENV VITE_SENTRY_ENVIRONMENT=$VITE_SENTRY_ENVIRONMENT
ENV VITE_FEEDBACK_URL=$VITE_FEEDBACK_URL
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Stage 2: Backend + serve frontend
FROM python:3.12-slim
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY --from=frontend-build /app/frontend/dist ./static

# Ejecuta como usuario no-root en runtime (reduce la superficie de ataque en prod).
# El proceso no escribe en disco: alembic solo lee migraciones, uvicorn sirve, y el
# frontend estático se lee. Los archivos copiados quedan legibles para todos (755/644).
RUN useradd --create-home --uid 10001 appuser
USER appuser

ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "alembic upgrade head && python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
