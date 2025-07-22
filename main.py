from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from models import Base, engine
from typing import Optional
from github_scanner import github_search_manually
from datetime import datetime, timedelta

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "GitHub Monitor running"}

@app.get("/search")
async def github_search(
    keyword: str = Query(..., description="Search keyword"),
    language: str = Query(None, description="Language Programming"),
    since: str = Query(default=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))
):
    results, filename = await github_search_manually(keyword, language, since)
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return JSONResponse(content=results, headers=headers)
