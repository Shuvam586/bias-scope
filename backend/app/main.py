from backend.app.ingestion.rss import fetch_feed
from backend.app.ingestion.sources import SOURCES
from backend.app.db.supabase_client import insert_articles

# for source in SOURCES.values():
#     print(source["name"])
#     print()

#     for f in source["feeds"]:
#         print(f)
#         insert_articles(fetch_feed(f, source["name"]))

#     print()

insert_articles(fetch_feed("https://theprint.in/feed", "The Print"))