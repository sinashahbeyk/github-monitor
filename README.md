﻿# github-monitor

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate      # Linux
venv\Scripts\activate.bat     # Windows

# Install dependencies
pip install -r requirements.txt


# Start the Service
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# API will be accessible at:
http://localhost:8000/docs (Swagger UI)
http://localhost:8000/redoc (ReDoc UI)

# Direct URL Example
"http://localhost:8000/search?keyword=&language=&since="


# Use in External Systems
import requests

res = requests.get("http://localhost:8000/search", params={
    "keyword": "",
    "language": "",
    "since": ""
})
data = res.json()
print("Found", len(data), "repos")
