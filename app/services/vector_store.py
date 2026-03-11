from functools import lru_cache

try:
    import chromadb
except ImportError:  # pragma: no cover - optional at test time
    chromadb = None

_STORE: dict[str, dict] = {}


class VectorStoreService:
    def __init__(self) -> None:
        self._client = chromadb.Client() if chromadb else None
        self._collection = (
            self._client.get_or_create_collection(name="salesforce_success_cases")
            if self._client
            else None
        )

    def upsert_cases(self, items: list[dict]) -> int:
        if not items:
            return 0
        if self._collection:
            self._collection.upsert(
                ids=[item["opportunity_id"] for item in items],
                documents=[item["document"] for item in items],
                metadatas=[item["metadata"] for item in items],
            )
            return len(items)
        for item in items:
            _STORE[item["opportunity_id"]] = {
                "document": item["document"],
                "metadata": item["metadata"],
            }
        return len(items)

    def query_similar_cases(self, filters: dict, limit: int = 3) -> list[dict]:
        if self._collection:
            results = self._collection.get(include=["documents", "metadatas"])
            scored = []
            for case_id, document, metadata in zip(
                results.get("ids", []),
                results.get("documents", []),
                results.get("metadatas", []),
            ):
                scored.append(
                    {
                        "id": case_id,
                        "document": document,
                        "metadata": metadata,
                        "score": _score_case(metadata, filters),
                    }
                )
            return sorted(scored, key=lambda item: item["score"], reverse=True)[:limit]

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


def _score_case(metadata: dict, filters: dict) -> int:
    score = 0
    if metadata.get("family") == filters.get("family"):
        score += 2
    if metadata.get("rival") == filters.get("rival"):
        score += 1
    score += _numeric_similarity(metadata.get("amount"), filters.get("amount"))
    score += _numeric_similarity(metadata.get("income"), filters.get("income"))
    return score


def _numeric_similarity(left, right) -> int:
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


def upsert_cases(items: list[dict]) -> int:
    return get_vector_store_service().upsert_cases(items)


def query_similar_cases(filters: dict, limit: int = 3) -> list[dict]:
    return get_vector_store_service().query_similar_cases(filters, limit=limit)
