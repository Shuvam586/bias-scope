import feedparser as fp
from sources import SOURCES
from datetime import datetime 
from pydantic import BaseModel, HttpUrl


outlet = "ndtv"

class Article(BaseModel):
    title: str
    url: HttpUrl
    description: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    source: str

def fetch_feed(outlet: str) -> list[Article]:
    url = SOURCES[outlet]["feeds"][0]
    feed = fp.parse(url)

    # print(outlet, "\n")

    articles_list = []

    for entry in feed.entries:
        article = Article(
            title=entry.get("title"),
            url=entry.get("link"),
            description=entry.get("summary"),
            author=entry.get("author"),
            published_at=datetime.strptime(entry.get("published"),"%a, %d %b %Y %H:%M:%S %z"),
            source=SOURCES[outlet]["name"]
        )

        articles_list.append(article)

        # print(dir(entry.author))

    # print(*articles_list, sep="\n\n")

    return articles_list

fetch_feed(outlet=outlet)