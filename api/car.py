import json
import reellm

from fastapi import APIRouter
from pydantic import BaseModel


car_router = APIRouter()


class SeachRecipe(BaseModel):
    input_text: str
    knowledge: dict
    n_items: int = 3


@car_router.post("/search")
def search_cars(req: SeachRecipe):
    model = reellm.get_llm(reellm.ModelName.GPT_4_O)
    # Search cars models according to the user input
    recipe_name = model.invoke(
        [
            (
                "user",
                f"You role is to return {req.n_items} car models that match the user input. Be creative about the models, and return a JSON formatted as {{'search_result': ['car1', 'car2', 'car3']}}",
            ),
            ("user", f"Here is the user input : {req.input_text}"),
        ],
        temperature=0,
        response_format={"type": "json_object"},
    ).content

    recipe_name = json.loads(recipe_name)

    print(recipe_name)

    return {"search_result": recipe_name["search_result"]}
