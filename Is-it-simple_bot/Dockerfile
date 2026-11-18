FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY is_it_simple_bot.py .
CMD ["python", "is_it_simple_bot.py"]
