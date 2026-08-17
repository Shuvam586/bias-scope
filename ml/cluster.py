import json
import re
import numpy as np
import pandas as pd
import hdbscan

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

DATASET_PATH = "./dataset/news.jsonl"
MODEL_NAME = "all-MiniLM-L6-v2"
MAX_ARTICLES = None
EVENT_TEXT_WORDS = 900

HDBSCAN_MIN_CLUSTER_SIZE = 2
HDBSCAN_MIN_SAMPLES = 1

SEMANTIC_WEIGHT = 0.90
TIME_WEIGHT = 0.10

TIME_DECAY_DAYS = 30


print("\nLoading dataset...")
def load_dataset(path):
    if path.endswith(".jsonl"):
        records = []
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records
    else:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)


data = load_dataset(DATASET_PATH)
df = pd.DataFrame(data)

print("Articles loaded:", len(df))



required_columns = ["input_text", "date", "source"]
for column in required_columns:
    if column not in df.columns:
        raise ValueError( f"Dataset is missing column: {column}" )


df = df.dropna(subset=["input_text", "date"])
df["input_text"] = (df["input_text"].astype(str))
df["date"] = pd.to_datetime(df["date"], errors="coerce")

df = df.dropna(subset=["date"])
df = df[df["input_text"].str.strip() != ""]

df = df.reset_index(drop=True)



if MAX_ARTICLES is not None:
    df = df.head(MAX_ARTICLES).copy()
    df = df.reset_index(drop=True)

print("Articles being processed:", len(df))



def clean_text(text):
    text = re.sub( r"<[^>]+>", " ", text)
    text = re.sub( r"https?://\S+|www\.\S+", " ", text)
    text = re.sub( r"\s+", " ", text)

    return text.strip()

df["clean_text"] = (df["input_text"].apply(clean_text))



before = len(df)
df = df.drop_duplicates(subset=["clean_text"])
df = df.reset_index(drop=True)

print("Duplicate articles removed:", before - len(df))



def get_event_text(text, word_limit=900):
    words = text.split()
    return " ".join(words[:word_limit])


print("\nLoading Sentence Transformer...")
model = SentenceTransformer(MODEL_NAME)

print("Model loaded.")
print("\nGenerating article embeddings...")

article_embeddings = []
for index, row in df.iterrows():
    text = row["clean_text"]
    event_text = get_event_text(text, EVENT_TEXT_WORDS)
    article_embedding = model.encode(event_text,show_progress_bar=False)

    article_embeddings.append(article_embedding)

    if (index + 1) % 50 == 0:
        print(f"Processed {index + 1}/{len(df)}")


article_embeddings = np.array(article_embeddings)

print("\nEmbedding shape:", article_embeddings.shape)
print("\nCalculating semantic similarity...")
semantic_similarity = cosine_similarity(article_embeddings)

print("\n")
print("=" * 70)
print("CALCULATING TEMPORAL SIMILARITY")
print("=" * 70)

dates = df["date"].values
number_of_articles = len(df)
temporal_similarity = np.zeros((
        number_of_articles,
        number_of_articles
    )
)

for i in range(number_of_articles):
    for j in range(number_of_articles):
        days_difference = abs((dates[i] - dates[j])
            .astype(
                "timedelta64[D]")
            .astype(int)
        )

        temporal_similarity[i][j] = np.exp(-days_difference / TIME_DECAY_DAYS)

print("Temporal similarity calculated.")

print("\n")
print("=" * 70)
print("CREATING COMBINED SIMILARITY")
print("=" * 70)

combined_similarity = (SEMANTIC_WEIGHT * semantic_similarity + TIME_WEIGHT * temporal_similarity)

print(f"Semantic weight: {SEMANTIC_WEIGHT}")
print(f"Time weight: {TIME_WEIGHT}")
print(f"Time decay: {TIME_DECAY_DAYS} days")

combined_distance = (1 - combined_similarity)
combined_distance = np.clip(combined_distance, 0, 1)

print("\n")
print("=" * 70)
print("HDBSCAN CLUSTERING")
print("=" * 70)

hdbscan_model = hdbscan.HDBSCAN(
    min_cluster_size=HDBSCAN_MIN_CLUSTER_SIZE,
    min_samples=HDBSCAN_MIN_SAMPLES,
    metric="precomputed"
)

hdbscan_labels = (
    hdbscan_model.fit_predict(
        combined_distance
    )
)

num_clusters = (len(set(hdbscan_labels)) - (1 if -1 in hdbscan_labels else 0))

num_noise = np.sum(
    hdbscan_labels == -1
)

print("HDBSCAN clusters:", num_clusters)
print("Noise articles:", num_noise)

next_cluster = hdbscan_labels.max() + 1

for i in range(len(hdbscan_labels)):
    if hdbscan_labels[i] == -1:
        hdbscan_labels[i] = next_cluster
        next_cluster += 1

df["cluster"] = (
    hdbscan_labels
)

print("Final event clusters:", len(df["cluster"].unique()))

def display_clusters(df, cluster_column, title):
    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)

    clusters = sorted(
        df[cluster_column].unique()
    )

    for cluster in clusters:
        cluster_articles = df[
            df[cluster_column] == cluster
        ]

        print(f"\nCLUSTER {cluster}")
        print("-" * 50)

        for _, article in (cluster_articles.iterrows()):
            print("Date:", article["date"].date())
            print("Source:", article["source"])
            print("Text:", article["clean_text"][:250])
            print()


display_clusters(
    df,
    "cluster",
    "FINAL EVENT CLUSTERS"
)

print("\n")
print("Clustering completed")