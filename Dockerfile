
#Use python 3.10+
FROM python:3.10-slim

#Setting working directory
WORKDIR /app

#Setting python path to the app
ENV PYTHONPATH=/app 

#installing requirements 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#opening port 8000 for fastapi access
EXPOSE 8000

# Copy project folders
COPY src/ ./src/
COPY configs/ ./configs/ 

CMD [ "uvicorn","src.main:app", "--host","0.0.0.0","--port","8000" ]