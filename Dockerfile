FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN python -m venv /opt/venv
COPY services/api/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --requirement /tmp/requirements.txt

RUN addgroup --system flowbeacon && adduser --system --ingroup flowbeacon flowbeacon \
    && mkdir -p /app/services/api /app/services/web /data \
    && chown -R flowbeacon:flowbeacon /app /data
COPY --chown=flowbeacon:flowbeacon services/api /app/services/api
COPY --chown=flowbeacon:flowbeacon services/web /app/services/web

USER flowbeacon
WORKDIR /app/services/api
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
