from openai import OpenAI

from app.core.config import settings


class EmbeddingService:
    MODEL = "text-embedding-3-small"

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.MODEL, input=text)
        return response.data[0].embedding
