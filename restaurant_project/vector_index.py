"""ChromaDB multimodal index and retrieval demonstrations for Q4–Q6."""

from __future__ import annotations

import math
import re
from typing import Any

from restaurant_project.data import ARTICLE_DOCUMENTS, IMAGE_DOCUMENTS

EMBEDDING_VOCABULARY = sorted(
    {
        token
        for entry in ARTICLE_DOCUMENTS + IMAGE_DOCUMENTS
        for token in re.findall(r"[a-z0-9]+", entry["text"].casefold())
    }
)
VOCABULARY_INDEX = {token: index for index, token in enumerate(EMBEDDING_VOCABULARY)}
VECTOR_SIZE = len(EMBEDDING_VOCABULARY)


def embed_text(text: str) -> list[float]:
    """Create reproducible bag-of-words vectors without downloading a model."""
    vector = [0.0] * VECTOR_SIZE
    tokens = re.findall(r"[a-z0-9]+", text.casefold())
    for token in tokens:
        index = VOCABULARY_INDEX.get(token)
        if index is not None:
            vector[index] += 1.0
    norm = math.sqrt(sum(value * value for value in vector))
    if norm:
        return [value / norm for value in vector]
    return vector


def build_multimodal_vector_index() -> tuple[Any, Any, Any]:
    import chromadb
    from chromadb.config import Settings

    client = chromadb.Client(Settings(anonymized_telemetry=False, is_persistent=False))
    restaurant_articles = client.get_or_create_collection(
        name="restaurant_articles", metadata={"hnsw:space": "cosine"}
    )
    food_images = client.get_or_create_collection(
        name="food_images", metadata={"hnsw:space": "cosine"}
    )
    for collection, entries in (
        (restaurant_articles, ARTICLE_DOCUMENTS),
        (food_images, IMAGE_DOCUMENTS),
    ):
        collection.add(
            ids=[entry["id"] for entry in entries],
            documents=[entry["text"] for entry in entries],
            metadatas=[entry["metadata"] for entry in entries],
            embeddings=[embed_text(entry["text"]) for entry in entries],
        )
    print(f"Created Chroma collection: {restaurant_articles.name}")
    print(f"Created Chroma collection: {food_images.name}")
    print("Multimodal Vector Index Construction COMPLETE")
    return client, restaurant_articles, food_images


def run_similarity_retrieval(collection: Any, query: str) -> dict[str, Any]:
    print(f"\nRetrieval query: {query!r} (metadata filter: cuisine = Peruvian)")
    results = collection.query(
        query_embeddings=[embed_text(query)],
        n_results=3,
        where={"cuisine": {"$eq": "Peruvian"}},
        include=["documents", "metadatas", "distances"],
    )
    for rank, (document, metadata, distance) in enumerate(
        zip(results["documents"][0], results["metadatas"][0], results["distances"][0]),
        start=1,
    ):
        print(
            f"{rank}. {metadata['restaurant_id']} | distance={distance:.3f} | {document}"
        )
    print("Similarity Retrieval with Metadata Filtering COMPLETE")
    return results


def _rank_collection(collection: Any, query: str) -> dict[str, float]:
    results = collection.query(
        query_embeddings=[embed_text(query)],
        n_results=3,
        include=["metadatas", "distances"],
    )
    return {
        metadata["restaurant_id"]: 1.0 - distance
        for metadata, distance in zip(
            results["metadatas"][0], results["distances"][0]
        )
    }


def run_fusion_demo(articles: Any, images: Any, query: str) -> list[dict[str, Any]]:
    article_scores = _rank_collection(articles, query)
    image_scores = _rank_collection(images, query)
    restaurant_ids = set(article_scores) | set(image_scores)
    configurations = ((0.8, 0.2), (0.5, 0.5), (0.2, 0.8))
    print(f"\nMultimodal fusion query: {query!r}")
    all_results = []
    for article_weight, image_weight in configurations:
        ranked = sorted(
            (
                {
                    "restaurant_id": restaurant_id,
                    "score": article_weight * article_scores.get(restaurant_id, 0.0)
                    + image_weight * image_scores.get(restaurant_id, 0.0),
                }
                for restaurant_id in restaurant_ids
            ),
            key=lambda result: result["score"],
            reverse=True,
        )
        all_results.append(
            {
                "weights": {"articles": article_weight, "images": image_weight},
                "ranking": ranked,
            }
        )
        print(
            f"weights articles={article_weight:.1f}, images={image_weight:.1f}: "
            + ", ".join(
                f"{item['restaurant_id']} ({item['score']:.3f})" for item in ranked
            )
        )
    print("Multimodal Similarity Fusion and Retrieval Ranking COMPLETE")
    return all_results


def main() -> None:
    _, articles, images = build_multimodal_vector_index()
    run_similarity_retrieval(articles, "Peruvian restaurant with ceviche")
    run_fusion_demo(articles, images, "casual seafood restaurant")


if __name__ == "__main__":
    main()
