import chromadb

_client = chromadb.Client()
_collection = _client.get_or_create_collection("sales_cases")


def get_collection():
    return _collection


# TODO: implement embed / query helpers
