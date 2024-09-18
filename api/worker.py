from fastapi import APIRouter
from pydantic import BaseModel
import json

from objects.AI_model import get_ai_model

worker_router = APIRouter()


class SearchWorker(BaseModel):
    input_text: str
    knowledge: dict
    n_items: int = 3


@worker_router.post("/search")
def search_hotels(req: SearchWorker):
    model = get_ai_model()
    # Search cars models according to the user input
    worker_name = (
        model()
        .invoke(
            [
                (
                    "user",
                    f"You role is to return {req.n_items} construction worker that match the user input for their project. Be creative about the workers and what type of service they provide, and return a JSON formatted as {{'search_result': ['worker1', 'worker2', 'worker3']}}",
                ),
                ("user", f"Here is the user input : {req.input_text}"),
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        .content
    )

    recipe_name = json.loads(worker_name)

    print(recipe_name)

    return {"search_result": recipe_name["search_result"]}


@worker_router.post("/add")
def add_quote(req: SearchWorker):
    model = get_ai_model()
    # Search cars models according to the user input
    worker_name = (
        model()
        .invoke(
            [
                (
                    "user",
                    f"Your role is to determine with the information if this type work can be done for the client. No need to have precise information. Be creative about the reason why a job can or can't be done and return a JSON formatted as {{'search_result': ['yes with explanations']}}, or {{'search_result': ['no with explanations']}}"
                    f"Here is the information : {req.knowledge}",
                ),
                ("user", f"Here is the user input : {req.input_text}"),
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        .content
    )

    recipe_name = json.loads(worker_name)

    print(recipe_name)

    return {"search_result": recipe_name["search_result"]}


@worker_router.post("/yesno")
def yesno(req: SearchWorker):
    model = get_ai_model()
    worker_name = (
        model()
        .invoke(
            [
                (
                    "user",
                    "Your role is to return if we should answer yes or no based on the information, just answer loosely if it's possible. Return a JSON formatted as {{'search_result': ['yes with explanations']}}, or {{'search_result': ['no with explanations']}}",
                    f"Here is the information : {req.knowledge}",
                ),
                ("user", f"Here is the user input : {req.input_text}"),
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        .content
    )
    recipe_name = json.loads(worker_name)

    print(recipe_name)

    return {"search_result": recipe_name["search_result"]}
