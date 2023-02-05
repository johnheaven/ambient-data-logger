FROM python:3.11-alpine
WORKDIR /usr/src
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "./src/ambient-data-logger.py"]
