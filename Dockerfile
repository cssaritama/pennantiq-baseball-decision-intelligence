FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements-llm.txt ./
RUN pip install --no-cache-dir -r requirements-llm.txt

COPY . .
RUN mkdir -p data/runtime evaluation/results

EXPOSE 8501

HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"

CMD ["streamlit","run","app.py","--server.address=0.0.0.0","--server.port=8501"]
