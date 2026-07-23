FROM python:3.12.11-slim-bookworm

ARG APP_VERSION=dev
ARG COMMIT_SHA=unknown

ENV APP_VERSION="${APP_VERSION}" \
    COMMIT_SHA="${COMMIT_SHA}" \
    HOST=0.0.0.0 \
    PORT=8080 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

COPY --chown=app:app app/ ./app/

USER 10001:10001
EXPOSE 8080

ENTRYPOINT ["python", "-m", "app.server"]
