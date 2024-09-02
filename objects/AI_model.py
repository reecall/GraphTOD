from langchain_openai import AzureChatOpenAI, ChatOpenAI
from dotenv import load_dotenv
from os import environ


class AIModel:
    def __init__(self):
        # Set default model
        load_dotenv(override=True)
        if environ.get("DEFAULT_OPENAI_TYPE").lower() == "openai":
            self.model = ChatOpenAI(
                model=environ.get("DEFAULT_OPENAI_MODEL"),
                api_key=environ.get("DEFAULT_OPENAI_API_KEY"),
            )
        elif environ.get("DEFAULT_OPENAI_TYPE").lower() == "azure_openai":
            self.model = AzureChatOpenAI(
                model=environ.get("DEFAULT_OPENAI_DEPLOYMENT_NAME"),
                azure_endpoint=environ.get("DEFAULT_OPENAI_ENDPOINT"),
                api_key=environ.get("DEFAULT_OPENAI_API_KEY"),
            )
        else:
            raise ValueError("Invalid model type")
        # test if the model is working
        self.model.invoke(
            "test",
            temperature=0,
            max_tokens=1,
        )
        self.is_default = True

    def __call__(self):
        return self.model

    def set_model(
        self,
        type,
        model_name,
        api_key,
        endpoint=None,
    ):
        if type.lower() == "openai":
            self.is_default = False
            self.model = ChatOpenAI(model=model_name, api_key=api_key)
        elif type.lower() == "azure_openai":
            self.is_default = False
            self.model = AzureChatOpenAI(
                model=model_name,
                azure_endpoint=endpoint,
                api_key=api_key,
            )
        else:
            raise ValueError("Invalid model type")


AI_model = AIModel()


def get_ai_model() -> AIModel:
    return AI_model
