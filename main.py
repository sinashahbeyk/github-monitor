from models import Base, engine
from fastapi import FastAPI, Query
from scheduler import start_scheduler
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
from github_scanner import github_search_manually

Base.metadata.create_all(bind=engine)

scheduler = start_scheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    print("INFO:     Monitoring started")
    yield
    scheduler.shutdown()
    print("INFO:     Monitoring shut down")


app = FastAPI(lifespan=lifespan)

@app.get("/")
def index():
    return {"message": "GitHub Monitoring"}

@app.get("/search")
async def github_search(
    keyword: str = Query(..., description="Search keyword"),
    language: str = Query(None, description="Language Programming"),
    since: str = Query(default=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))
):
    results, filename = await github_search_manually(keyword, language, since)
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return JSONResponse(content=results, headers=headers)
