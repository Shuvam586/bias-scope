from datetime import datetime
from pydantic import BaseModel, HttpUrl
from backend.app.ingestion.rss import fetch_feed
from backend.app.ingestion.sources import SOURCES
from backend.app.db.supabase_client import insert_articles
from ml.cluster import cluster_articles

class Article(BaseModel):
    id: str | None
    title: str
    url: HttpUrl
    description: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    source: str
    cluster: str | None

class Event(BaseModel):
    id: str | None
    title: str
    summary: str | None = None

for source in SOURCES.values():
    print(source["name"])
    print()

    allArticles = []

    for f in source["feeds"]:
        print(f)
        allArticles.extend(fetch_feed(f, source["name"]))

    results = cluster_articles(allArticles)

    insert_articles(results["articles"])

    print()
