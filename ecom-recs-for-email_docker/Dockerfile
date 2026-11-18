FROM python:3.11

COPY requirements.txt .
# LightFM's source release requires legacy setup and NumPy available at build time.
RUN pip install --no-cache-dir pip==24.3.1 setuptools==68.2.2 wheel==0.45.1 numpy==1.26.4 \
    && pip install --no-cache-dir --no-use-pep517 -r requirements.txt

WORKDIR /app

COPY main.py .
COPY settings.py .
COPY scripts/ ./scripts/

RUN chmod +x main.py

CMD [ "python", "./main.py" ]
