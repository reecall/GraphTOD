import chromadb
import pandas as pd
import uuid

from tqdm import tqdm
from reellm import get_embedding, ModelName
from dotenv import load_dotenv

load_dotenv(override=True)
large_embedder = get_embedding(ModelName.EMBEDDING_LARGE)
chroma_client = chromadb.PersistentClient(path="../chroma")

# read data/corpus_recipe.json as a dataframe
df = pd.read_json("corpus_recipe.jsonl", lines=True)
recipe_titles = df["title"].to_list()

# create a new collection named 'recipe'
recipe_collection = chroma_client.create_collection("recipe", get_or_create=True)

# insert the dataframe into the collection
recipe_collection.upsert(
    documents=df["title"].to_list(),
    embeddings=[large_embedder.embed_query(title) for title in tqdm(recipe_titles)],
    ids=[str(uuid.uuid4()) for _ in range(len(df))],
)
