import json

from fastapi import APIRouter
from pydantic import BaseModel
from objects.AI_model import get_ai_model


car_router = APIRouter()


class SearchCar(BaseModel):
    input_text: str
    knowledge: dict
    n_items: int = 3


@car_router.post("/search")
def search_cars(req: SearchCar):
    model = get_ai_model()
    # Search cars models according to the user input
    recipe_name = (
        model()
        .invoke(
            [
                (
                    "user",
                    f"You role is to return {req.n_items} car models that match the user input. Be creative about the models, and return a JSON formatted as {{'search_result': ['car1', 'car2', 'car3']}}",
                ),
                ("user", f"Here is the user input : {req.input_text}"),
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        .content
    )

    recipe_name = json.loads(recipe_name)

    print(recipe_name)

    return {"search_result": recipe_name["search_result"]}