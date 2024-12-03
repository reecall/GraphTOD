from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_community.chat_models.azureml_endpoint import (
    AzureMLChatOnlineEndpoint,
    CustomOpenAIChatContentFormatter,
)
from langchain_mistralai.chat_models import ChatMistralAI
from dotenv import load_dotenv
from os import environ


class AIModel:
    def __init__(self):
        # Set default model
        load_dotenv(override=True)
        # Get model type
        model_type = environ.get("DEFAULT_OPENAI_TYPE")
        if model_type is None:
            self.is_default = False
            self.model = None
            return
        elif model_type.lower() == "openai":
            self.model = ChatOpenAI(
                model=environ.get("DEFAULT_OPENAI_MODEL"),
                api_key=environ.get("DEFAULT_OPENAI_API_KEY"),
            )
        elif model_type.lower() == "azure_openai":
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
        model_name=None,
        api_key=None,
        endpoint=None,
    ):  # à préciser : set model a besoin d'avoir param def pour openai, pour mistral c'est pas nécessaire
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
        elif type.lower() == "llama":
            self.is_default = False
            self.model = AzureMLChatOnlineEndpoint(
                deployment_name=environ.get("LLAMA_3_70B_DEPNAME"),
                endpoint_api_key=environ.get("LLAMA3_70B_API_KEY"),
                endpoint_url=environ.get("LLAMA3_70B_API_ENDPOINT"),
                endpoint_api_type="serverless",
                content_formatter=CustomOpenAIChatContentFormatter(),
                timeout=360,
            )
        elif type.lower() == "mistral":
            self.is_default = False
            self.model = ChatMistralAI(
                model=environ.get("MISTRAL_LARGE_DEPNAME"), timeout=360
            )
        elif type.lower() == "cohere":
            self.is_default = False
            self.model = AzureMLChatOnlineEndpoint(
                deployment_name=environ.get("COMMAND_R_PLUS_DEPNAME"),
                endpoint_api_key=environ.get("COMMAND_R_PLUS_API_KEY"),
                endpoint_url=environ.get("COMMAND_R_PLUS_API_ENDPOINT"),
                endpoint_api_type="serverless",
                content_formatter=CustomOpenAIChatContentFormatter(),
                timeout=360,
            )
            self.model.invoke("test")
        else:
            raise ValueError("Invalid model type")


AI_model = AIModel()


def get_ai_model() -> AIModel:
    return AI_model
