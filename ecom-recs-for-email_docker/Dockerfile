FROM python:3.9

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY main.py .
COPY settings.py .
COPY scripts/ ./scripts/

RUN chmod +x main.py

CMD [ "python", "./main.py" ]
