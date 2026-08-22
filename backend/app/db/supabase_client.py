import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
from pydantic import BaseModel, HttpUrl

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
    image: str

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def insert_articles(articles: list[Article]):

    queue = []

    print(f"inserting {len(articles)} articles")

    for index, arti in enumerate(articles):
        queue.append(arti.model_dump(mode="json", exclude_none=True))

        if ((index+1)%10==0):
            response = supabase.table("articles").insert(queue).execute()
            queue = []

    if (len(queue)!=0):
        response = supabase.table("articles").insert(queue).execute()


def insert_clusters(events: list[Event]):

    allEvents = []

    for index, eve in enumerate(events):
        allEvents.append(eve.model_dump(mode="json", exclude_none=True))

    response = supabase.table("events").insert(allEvents).execute()

    pass