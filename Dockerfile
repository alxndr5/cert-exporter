FROM python:slim

RUN pip install cryptography pyyaml kubernetes aiohttp PyOpenSSL
COPY src /app
WORKDIR /app
USER 9000
CMD ["python", "-u", "exporter.py"]
