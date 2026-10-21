FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/Hafsa-Anwar65/pkphone"
LABEL org.opencontainers.image.description="Clean, validate and normalize Pakistani phone numbers."
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir . && rm -rf /app

# Mount your files here to clean a CSV: -v "$PWD:/data"
WORKDIR /data
ENTRYPOINT ["pkphone"]
CMD ["--help"]
