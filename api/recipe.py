import chromadb
import reellm
import pandas as pd

from fastapi import APIRouter
from pydantic import BaseModel


recipe_router = APIRouter()


class SeachRecipe(BaseModel):
    input_text: str
    knowledge: dict
    n_items: int = 3


@recipe_router.post("/search")
def search_recipe(req: SeachRecipe):
    model = reellm.get_llm(reellm.ModelName.MIXTRAL_8X22B)
    # Extract the recipe name from the user input
    if not req.knowledge.get("search_result"):
        recipe_name = model.invoke(
            [
                (
                    "system",
                    "Your role is to extract only the food name from the input sentence of the user.\nReturn only the extracted plate of food type that you find in the input and nothing else.",
                ),
                ("user", req.input_text),
            ],
            temperature=0,
            max_tokens=6,
        ).content
        req.knowledge["searched_recipe"] = recipe_name
        print(f"Recipe extracted: {recipe_name}")
    else:
        recipe_name = req.knowledge.get("searched_recipe")

    client = chromadb.PersistentClient()
    recipe_collection = client.get_collection("recipe")
    embedder = reellm.get_embedding(reellm.ModelName.EMBEDDING_LARGE)
    result = recipe_collection.query(
        embedder.embed_query(recipe_name), n_results=req.n_items
    )
    # print finded recipes
    print(result["documents"][0])
    return {"search_result": result["documents"][0]}


class SuggestRecipe(BaseModel):
    input_text: str
    n_items: int = 3


@recipe_router.post("/suggest")
def suggest_recipe(req: SeachRecipe):
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
        new_recipes = suggest_recipe(None, n_items=2)["search_result"]
    found_recipes = req.knowledge["search_result"]
    return {"search_result": found_recipes + new_recipes}
