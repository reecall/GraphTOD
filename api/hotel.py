from fastapi import APIRouter
from pydantic import BaseModel
import json

from objects.AI_model import get_ai_model


hotel_router = APIRouter()


class SearchHotel(BaseModel):
    input_text: str
    knowledge: dict
    n_items: int = 3


@hotel_router.post("/search")
def search_hotels(req: SearchHotel):
    model = get_ai_model()
    # Search cars models according to the user input
    hotel_names = (
        model()
        .invoke(
            [
                (
                    "user",
                    f"You role is to return {req.n_items} hotels that match the user input. Be creative about the hotels and what type of accomodation they provide, and return a JSON formatted as {{'search_result': ['hotel1', 'hotel2', 'hotel3']}}",
                ),
                ("user", f"Here is the user input : {req.input_text}"),
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        .content
    )

    hotel_names = json.loads(hotel_names)

    print(hotel_names)
    if "search_result" in req.knowledge:
        return {
            "search_result": req.knowledge["search_result"]
            + hotel_names["search_result"]
        }
    return {"search_result": hotel_names["search_result"]}
