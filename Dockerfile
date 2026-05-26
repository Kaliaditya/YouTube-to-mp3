FROM python:3.12

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg

# App folder
WORKDIR /app

# Copy files
COPY . .

# Install Python packages
RUN pip install -r requirements.txt

# Start FastAPI
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port=$PORT"]
