import asyncio, os, json
from models import Base, engine
from datetime import datetime, timedelta
from models import SessionLocal, Repository
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from github_scanner import github_monitor, match_exact_keyword

Base.metadata.create_all(bind=engine)

MONITORED_KEYWORDS = ["edr", "malware]
MONITORED_LANGUAGES = ["python", "go"]

async def save_if_not_exists(repo, keyword):
    db = SessionLocal()
    if not db.query(Repository).filter_by(id=repo["id"]).first():
        repo_obj = Repository(
            id=repo["id"], name=repo["name"], full_name=repo["full_name"],
            url=repo["url"], description=repo["description"], language=repo["language"],
            created_at=datetime.fromisoformat(repo["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(repo["updated_at"].replace("Z", "+00:00")),
            keyword=keyword
        )
        db.add(repo_obj)
        db.commit()
    db.close()

async def daily_monitor():
    since = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{datetime.now()}] Starting daily scan since {since}")
    for keyword in MONITORED_KEYWORDS:
        for language in MONITORED_LANGUAGES:
            repos = await github_monitor(keyword, language, since)
            matches = [r for r in repos if match_exact_keyword(r, keyword)]
            os.makedirs("github_monitor", exist_ok=True)
            date_str = datetime.now().strftime("%Y-%m-%d")
            fname = f"{keyword}_{language}_{date_str}.json"
            with open(os.path.join("github_monitor", fname), "w", encoding="utf-8") as f:
                json.dump(matches, f, ensure_ascii=False, indent=2)

            await asyncio.gather(*(save_if_not_exists(r, keyword) for r in matches))


def start_scheduler():
    scheduler = AsyncIOScheduler()
    trigger = CronTrigger(hour=9, minute=30, timezone="Asia/Tehran")
    scheduler.add_job(daily_monitor, trigger,
                      id="daily_github_monitor",
                      replace_existing=True, 
                      misfire_grace_time=3600
                      )  
    return scheduler


if __name__ == "__main__":
    asyncio.run(daily_monitor())
