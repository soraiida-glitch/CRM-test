from functools import lru_cache
from typing import Any

from openai import OpenAI

from app.config import settings

try:
    import chromadb
except ImportError:  # pragma: no cover - optional at test time
    chromadb = None

_STORE: dict[str, dict[str, Any]] = {}


class VectorStoreService:
    def __init__(self) -> None:
        self._embedding_client = OpenAI(api_key=settings.openai_api_key) if settings.has_openai else None
        self._client = chromadb.Client() if chromadb else None
        self._collection = (
            self._client.get_or_create_collection(name="salesforce_success_cases")
            if self._client
            else None
        )

    def upsert_cases(self, items: list[dict[str, Any]]) -> int:
        if not items:
            return 0

        if self._collection:
            payload = {
                "ids": [item["opportunity_id"] for item in items],
                "documents": [item["document"] for item in items],
                "metadatas": [item["metadata"] for item in items],
            }
            embeddings = self._embed_documents([item["search_text"] for item in items])
            if embeddings:
                payload["embeddings"] = embeddings
            self._collection.upsert(**payload)
            return len(items)

        for item in items:
            _STORE[item["opportunity_id"]] = {
                "document": item["document"],
                "metadata": item["metadata"],
                "search_text": item["search_text"],
            }
        return len(items)

    def query_similar_cases(self, filters: dict[str, Any], limit: int = 3) -> list[dict[str, Any]]:
        if self._collection:
            query_text = _build_search_text(filters)
            query_embeddings = self._embed_documents([query_text])
            if query_embeddings:
                results = self._collection.query(
                    query_embeddings=query_embeddings,
                    n_results=limit,
                    include=["documents", "metadatas", "distances"],
                )
                return _format_chroma_results(results)

            results = self._collection.get(include=["documents", "metadatas"])
            return _rank_metadata_results(results, filters, limit)

        return _rank_memory_results(filters, limit)

    def _embed_documents(self, documents: list[str]) -> list[list[float]] | None:
        if not self._embedding_client or not documents:
            return None
        response = self._embedding_client.embeddings.create(
            model="text-embedding-3-small",
            input=documents,
        )
        return [item.embedding for item in response.data]


def _build_search_text(payload: dict[str, Any]) -> str:
    parts = [
        str(payload.get("name", "")).strip(),
        str(payload.get("stage", "")).strip(),
        str(payload.get("family", "")).strip(),
        str(payload.get("description", "")).strip(),
    ]
    if payload.get("amount") is not None:
        parts.append(f"amount:{payload['amount']}")
    if payload.get("income") is not None:
        parts.append(f"income:{payload['income']}")
    parts.append(f"rival:{bool(payload.get('rival'))}")
    return " ".join(part for part in parts if part)


def _format_chroma_results(results: dict[str, Any]) -> list[dict[str, Any]]:
    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    formatted = []
    for case_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
        formatted.append(
            {
                "id": case_id,
                "document": document,
                "metadata": metadata,
                "score": round(1 - float(distance), 4),
            }
        )
    return formatted


def _rank_metadata_results(results: dict[str, Any], filters: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    ids = results.get("ids", [])
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    scored = []
    for case_id, document, metadata in zip(ids, documents, metadatas):
        scored.append(
            {
                "id": case_id,
                "document": document,
                "metadata": metadata,
                "score": _score_case(metadata, filters),
            }
        )
    return sorted(scored, key=lambda item: item["score"], reverse=True)[:limit]


def _rank_memory_results(filters: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    scored = []
    for case_id, item in _STORE.items():
        scored.append(
            {
                "id": case_id,
                "document": item["document"],
                "metadata": item["metadata"],
                "score": _score_case(item["metadata"], filters),
            }
        )
    return sorted(scored, key=lambda item: item["score"], reverse=True)[:limit]


def _score_case(metadata: dict[str, Any], filters: dict[str, Any]) -> int:
    score = 0
    if metadata.get("family") == filters.get("family"):
        score += 2
    if metadata.get("rival") == filters.get("rival"):
        score += 1
    score += _numeric_similarity(metadata.get("amount"), filters.get("amount"))
    score += _numeric_similarity(metadata.get("income"), filters.get("income"))
    return score


def _numeric_similarity(left: Any, right: Any) -> int:
    if left is None or right is None:
        return 0
    if left == right:
        return 2
    ratio = min(left, right) / max(left, right)
    if ratio >= 0.8:
        return 1
    return 0


@lru_cache
def get_vector_store_service() -> VectorStoreService:
    return VectorStoreService()


def upsert_cases(items: list[dict[str, Any]]) -> int:
    return get_vector_store_service().upsert_cases(items)


def query_similar_cases(filters: dict[str, Any], limit: int = 3) -> list[dict[str, Any]]:
    return get_vector_store_service().query_similar_cases(filters, limit=limit)
