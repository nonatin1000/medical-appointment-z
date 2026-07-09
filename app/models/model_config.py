from typing import TypedDict


class ModelConfig(TypedDict):
    api_key: str
    http_referer: str
    x_title: str
    models: list[str]
    temperature: float
