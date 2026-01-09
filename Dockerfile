
#Use python 3.10+
FROM python:3.10-slim

#Setting working directory
WORKDIR /app

#Setting python path to the app
ENV PYTHONPATH=/app 

#installing requirements 
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#installing testing requirements
RUN pip install -U pytest httpx

#opening port 8000 for fastapi access
EXPOSE 8000

# Copy project folders
COPY src/ ./src/
COPY configs/ ./configs/ 
COPY tests/ ./tests/

CMD [ "uvicorn","src.main:app", "--host","0.0.0.0","--port","8000" ]

# Set Hugging Face model cache directory
ENV HF_HOME=/models/huggingface
ENV TRANSFORMERS_CACHE=/models/huggingface
