FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends file binutils \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY analyze.py .
ENTRYPOINT ["python", "analyze.py"]