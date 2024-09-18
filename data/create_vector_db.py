import chromadb
import pandas as pd
import uuid

from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv(override=True)
machine_types = ["doctor", "recipe"]
embedder = SentenceTransformer("all-mpnet-base-v2")
chroma_client = chromadb.PersistentClient(path="../chroma")

for mt in machine_types:
    # read data/corpus_recipe.json as a dataframe
    df = pd.read_json(f"corpus_{mt}.jsonl", lines=True)
    titles = df["title"].to_list()

    # create a new collection named 'mt'
    recipe_collection = chroma_client.create_collection(mt, get_or_create=True)

    # insert the dataframe into the collection
    recipe_collection.upsert(
        documents=df["title"].to_list(),
        embeddings=embedder.encode(titles, show_progress_bar=True),
        ids=[str(uuid.uuid4()) for _ in range(len(df))],
    )
