import asyncio, os, json
from models import Base, engine
from datetime import datetime, timedelta
from models import SessionLocal, Repository
from github_scanner import github_monitor, match_exact_keyword

Base.metadata.create_all(bind=engine)

MONITORED_KEYWORDS = ["edr"]
MONITORED_LANGUAGES = ["python", "c", "c++", "go"]

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

async def run_once():
    since = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    for kw in MONITORED_KEYWORDS:
        for lang in MONITORED_LANGUAGES:
            repos = await github_monitor(kw, lang, since)
            matched = [r for r in repos if match_exact_keyword(r, kw)]

            folder = "github_monitor"
            os.makedirs(folder, exist_ok=True)
            fname = f"{since.split('T')[0]}_{kw}_{lang}.json"
            with open(os.path.join(folder, fname), "w", encoding="utf-8") as f:
                json.dump(matched, f, indent=2)

            await asyncio.gather(*(save_if_not_exists(r, kw) for r in matched))


if __name__ == "__main__":
    asyncio.run(run_once())



# async def daily_monitor():
#     since = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
#     for kw in MONITORED_KEYWORDS:
#         for lang in MONITORED_LANGUAGES:
#             repos = await github_monitor(kw, lang, since)
#             matched = [r for r in repos if match_exact_keyword(r, kw)]

#             folder = "github_monitor"
#             os.makedirs(folder, exist_ok=True)
#             fname = f"{since.split('T')[0]}_{kw}_{lang}.json"
#             with open(os.path.join(folder, fname), "w") as f:
#                 json.dump(matched, f, indent=2)

#             await asyncio.gather(*(save_if_not_exists(r, kw) for r in matched))

# async def run_scheduler():
#     while True:
#         await daily_monitor()
#         await asyncio.sleep(86400)

# def start_scheduler():
#     loop = asyncio.get_event_loop()
#     loop.create_task(run_scheduler())
