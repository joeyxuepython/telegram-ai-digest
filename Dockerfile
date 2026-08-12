FROM python:3.11-slim

LABEL org.opencontainers.image.title="Telegram AI Digest"
LABEL org.opencontainers.image.description="AI-powered daily/weekly digests for busy Telegram groups"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

RUN mkdir -p data

EXPOSE 8080

# Default: run web dashboard
# Override: docker run ... tad run
CMD ["tad-web"]
