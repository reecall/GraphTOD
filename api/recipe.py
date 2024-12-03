import chromadb
import pandas as pd

from fastapi import APIRouter
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from objects.AI_model import get_ai_model


recipe_router = APIRouter()


class SeachRecipe(BaseModel):
    input_text: str
    knowledge: dict
    n_items: int = 3


@recipe_router.post("/search")
def search_recipe(req: SeachRecipe):
    model = get_ai_model()
    # Extract the recipe name from the user input
    if not req.knowledge.get("search_result"):
        recipe_name = (
            model()
            .invoke(
                [
                    (
                        "system",
                        "Your role is to extract only the food name from the input sentence of the user.\nReturn only the extracted plate of food type that you find in the input and nothing else.",
                    ),
                    ("user", req.input_text),
                ],
                temperature=0,
                max_tokens=20,
            )
            .content
        )
        req.knowledge["searched_recipe"] = recipe_name
        print(f"Recipe extracted: {recipe_name}")
    else:
        recipe_name = req.knowledge.get("searched_recipe")

    client = chromadb.PersistentClient(path="./chroma")
    recipe_collection = client.get_collection("recipe")
    embedder = SentenceTransformer("all-mpnet-base-v2")
    try:
        result = recipe_collection.query(
            embedder.encode(recipe_name).tolist(), n_results=req.n_items
        )
    except TypeError as e:
        print(recipe_name)
        print(e)
        return
    # print finded recipes
    print(result["documents"][0])
    return {"search_result": result["documents"][0]}


class SuggestRecipe(BaseModel):
    input_text: str
    knowledge: dict
    n_items: int = 3


@recipe_router.post("/suggest")
def suggest_recipe(req: SuggestRecipe):
    recipes = pd.read_json("data/corpus_recipe.jsonl", lines=True)
    # pick n_items random recipes
    result = recipes.sample(req.n_items)
    # keep only title
    result = result["title"].to_list()
    # print finded recipes
    print(result)
    return {"search_result": result}


class MoreResults(BaseModel):
    input_text: str
    knowledge: dict


@recipe_router.post("/more_results")
def more_results(req: MoreResults):
    # find two more recipes to show
    if req.knowledge.get("searched_recipe"):
        new_recipes = search_recipe(
            req.knowledge.get("searched_recipe"),
            n_items=len(req.knowledge["search_result"]) + 2,
        )["search_result"]
    else:
        suggest_req = SuggestRecipe(
            input_text=req.input_text, knowledge=req.knowledge, n_items=2
        )
        new_recipes = suggest_recipe(suggest_req)["search_result"]
    found_recipes = req.knowledge["search_result"]
    return {"search_result": found_recipes + new_recipes}
