FROM python:3.10-slim

COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

WORKDIR /app

COPY . /app

EXPOSE 8501

CMD ["streamlit", "run", "main.py"]