import chromadb
import reellm

from fastapi import APIRouter
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer


doctor_router = APIRouter()


class SearchDoctor(BaseModel):
    input_text: str
    knowledge: dict
    n_items: int = 3


@doctor_router.post("/search")
def search_recipe(req: SearchDoctor):
    model = reellm.get_llm(reellm.ModelName.MIXTRAL_8X22B)
    # Extract the recipe name from the user input
    if not req.knowledge.get("search_result"):
        doctor_name = model.invoke(
            [
                (
                    "system",
                    "Your role is to extract only the doctor name from the input sentence of the user.\nReturn only the extracted name that you find in the input and nothing else.",
                ),
                ("user", req.input_text),
            ],
            temperature=0,
            max_tokens=10,
        ).content
        req.knowledge["searched_doctor"] = doctor_name
        print(f"Doctor name extracted: {doctor_name}")
    else:
        doctor_name = req.knowledge.get("doctor_name")

    client = chromadb.PersistentClient(path="../chroma")
    recipe_collection = client.get_collection("doctor")
    embedder = SentenceTransformer("all-mpnet-base-v2")
    result = recipe_collection.query(
        embedder.encode(doctor_name).tolist(), n_results=req.n_items
    )
    # print finded recipes
    print(result["documents"][0])
    return {"search_result": result["documents"][0]}
