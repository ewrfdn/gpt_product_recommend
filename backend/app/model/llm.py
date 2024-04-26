import logging
import hashlib
from app.utils.tools import pick_value
from langchain_community.chat_models import ChatOpenAI

openai_params_field = [
    "model_name",
    "max_tokens",
    "n",
    "temperature",
    "top_p",
    "request_timeout",
]

logger = logging.getLogger(__name__)


def get_hashed_name(name):
    return hashlib.sha256(name.encode()).hexdigest()


class ModelFactory:
    @classmethod
    def get_model(cls, llm_config=None) -> ChatOpenAI:
        if llm_config is None:
            llm_config = {}
        return ChatOpenAI(**pick_value(llm_config, openai_params_field, filter_none=True))

    @classmethod
    def get_gpt4t_model(cls, max_token=1500, temperature=None, top_p=0.8) -> ChatOpenAI:
        return cls.get_model(
            llm_config={"model_name": "gpt-4", "max_token": max_token, 'temperature': temperature,
                        "top_p": top_p, "n": 1})

    @classmethod
    def get_gpt4_model(cls, max_token=1500, temperature=None, top_p=0.8) -> ChatOpenAI:
        return cls.get_model(
            llm_config={"model_name": "gpt-4-turbo-preview", "max_token": max_token, 'temperature': temperature,
                        "top_p": top_p, "n": 1})

    @classmethod
    def get_gpt35_model(cls, max_token=1000, temperature=None, top_p=0.8) -> ChatOpenAI:
        return cls.get_model(
            llm_config={"model_name": "gpt-3.5-turbo", "max_token": max_token, 'temperature': 0.8,
                        "n": 1})

    @classmethod
    def get_gpt35_16K_model(cls, max_token=1000, temperature=None, top_p=0.8) -> ChatOpenAI:
        return cls.get_model(
            llm_config={"model_name": "gpt-3.5-turbo-0125", "max_token": max_token, 'temperature': temperature,
                        "top_p": top_p, "n": 1})
