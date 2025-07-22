import aiohttp, os, json
from datetime import datetime
from models import Repository, SessionLocal

GITHUB_API = "https://api.github.com/search/repositories"
GITHUB_TOKEN = os.getenv("MONITOR_GITHUB_TOKEN")

HEADERS = {"Accept": "application/vnd.github+json",
           "Authorization": f"token {GITHUB_TOKEN}"}


def match_exact_keyword(repo, keyword):
    kw = keyword.lower()
    return any([
        kw in [w.lower() for w in repo["name"].split()],
        kw in [d.lower() for d in repo["description"].split()],
        kw in [t.lower() for t in repo["topics"]],
    ])

async def fetch(session, url):
    async with session.get(url, headers=HEADERS) as r:
        return await r.json() if r.status == 200 else None

async def github_monitor(keyword, language, since):
    query = f'{keyword} created:>{since} in:name,description,topics'
    if language:
        query += f' language:{language}'
    repos, page = [], 1
    async with aiohttp.ClientSession() as session:
        while True:
            url = f"{GITHUB_API}?q={query}&sort=updated&order=desc&page={page}&per_page=100"
            data = await fetch(session, url)
            if not data or not data.get("items"): break
            for r in data["items"]:
                repos.append({
                    "id": r["id"],
                    "name": r["name"],
                    "full_name": r["full_name"],
                    "url": r["html_url"],
                    "description": r.get("description") or "",
                    "language": r.get("language") or "",
                    "topics": r.get("topics") or [],
                    "created_at": r["created_at"],
                    "updated_at": r["updated_at"],
                    "keyword": keyword
                })
            page += 1
    return repos

async def github_search_manually(keyword, language, since):
    repos = await github_monitor(keyword, language, since)
    matched = [r for r in repos if match_exact_keyword(r, keyword)]

    folder = "github_search"
    os.makedirs(folder, exist_ok=True)
    ts = since.replace(":", "").replace("-", "")
    lang = language or "all"
    filename = f"{ts}_{keyword}_{lang}.json"
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(matched, f, ensure_ascii=False, indent=2)

    db = SessionLocal()
    for r in matched:
        if not db.query(Repository).filter_by(id=r["id"]).first():
            repo_obj = Repository(
                id=r["id"],
                name=r["name"],
                full_name=r["full_name"],
                url=r["url"],
                description=r["description"],
                language=r["language"],
                created_at=datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(r["updated_at"].replace("Z", "+00:00")),
                keyword=keyword
            )
            db.add(repo_obj)
    db.commit()
    db.close()
    return matched, filename
