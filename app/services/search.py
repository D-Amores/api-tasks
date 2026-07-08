from app.repositories.search import SearchRepository
from app.services.embedding import EmbeddingService


class SearchService:
    def __init__(self, repository: SearchRepository, embedder: EmbeddingService):
        self.repository = repository
        self.embedder = embedder

    def search(self, user_id: int, query: str, limit: int = 5):
        query_vector = self.embedder.embed(query)
        return self.repository.search_tasks(user_id, query_vector, limit)
