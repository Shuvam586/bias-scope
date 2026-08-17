import feedparser as fp
from datetime import datetime 
from pydantic import BaseModel, HttpUrl


outlet = "ndtv"

class Article(BaseModel):
    id: str | None
    title: str
    url: HttpUrl
    description: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    source: str
    cluster: str | None

def fetch_feed(outlet: str, source_name: str = "unknown") -> list[Article]:
    feed = fp.parse(outlet)

    # print(outlet, "\n")

    articles_list = []

    for entry in feed.entries:

        og_desc = entry.get("summary")
        if ">" in og_desc:
            rightmostgreaterthansymbollmao = len(og_desc)-1-og_desc[:-1].find(">")
            better_desc = og_desc[rightmostgreaterthansymbollmao+1:]
        else:
            better_desc = og_desc

        article = Article(
            id=None,
            title=entry.get("title"),
            url=entry.get("link"),
            description=better_desc,
            author=entry.get("author"),
            published_at=datetime.strptime(entry.get("published"),"%a, %d %b %Y %H:%M:%S %z"),
            source=source_name,
            cluster=None
        )

        articles_list.append(article)

        # print(dir(entry.author))

    # print(*articles_list, sep="\n\n")

    return articles_list

fetch_feed(outlet=outlet)