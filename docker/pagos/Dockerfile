FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/common ./common
COPY src/pagos ./pagos
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "pagos.main:app", "--host", "0.0.0.0", "--port", "8000"]
