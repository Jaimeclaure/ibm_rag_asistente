"""Small, fictional dataset shared by the lab demonstrations."""

from __future__ import annotations

RESTAURANT_PARAGRAPHS = [
    (
        "Andean Table is a Peruvian restaurant at 10 Main Street in Boston. "
        "It serves ceviche and lomo saltado in a casual dining room."
    ),
    (
        "Green Garden is a vegetarian Indian restaurant at 20 Oak Avenue in "
        "Boston, known for lentil curry and family-friendly service."
    ),
    (
        "Coastal Bowl is a Mexican restaurant at 5 Harbor Road in Cambridge. "
        "It serves tacos and fresh seafood in a casual setting."
    ),
]

RECIPES = [
    {"name": "Lomo saltado", "image_uri": "demo://lomo-saltado"},
    {"name": "Lentil curry", "image_uri": "demo://lentil-curry"},
    {"name": "Fish tacos", "image_uri": "demo://fish-tacos"},
]

RESTAURANTS = [
    {
        "id": "r1",
        "name": "Andean Table",
        "cuisine": "Peruvian",
        "city": "Boston",
        "description": "Ceviche and lomo saltado in a casual dining room.",
        "vegetarian": False,
        "price_level": 2,
    },
    {
        "id": "r2",
        "name": "Green Garden",
        "cuisine": "Indian",
        "city": "Boston",
        "description": "Vegetarian lentil curry with family-friendly service.",
        "vegetarian": True,
        "price_level": 1,
    },
    {
        "id": "r3",
        "name": "Coastal Bowl",
        "cuisine": "Mexican",
        "city": "Cambridge",
        "description": "Fresh seafood tacos in a casual setting.",
        "vegetarian": False,
        "price_level": 2,
    },
]

ARTICLE_DOCUMENTS = [
    {
        "id": "article-r1",
        "text": "Andean Table serves Peruvian ceviche and lomo saltado in Boston.",
        "metadata": {"restaurant_id": "r1", "cuisine": "Peruvian", "city": "Boston"},
    },
    {
        "id": "article-r2",
        "text": "Green Garden is a vegetarian Indian restaurant in Boston.",
        "metadata": {"restaurant_id": "r2", "cuisine": "Indian", "city": "Boston"},
    },
    {
        "id": "article-r3",
        "text": "Coastal Bowl serves Mexican seafood tacos in Cambridge.",
        "metadata": {"restaurant_id": "r3", "cuisine": "Mexican", "city": "Cambridge"},
    },
]

IMAGE_DOCUMENTS = [
    {
        "id": "image-r1",
        "text": "Demo caption: Peruvian stir-fried beef with rice and vegetables.",
        "metadata": {"restaurant_id": "r1", "cuisine": "Peruvian", "kind": "caption"},
    },
    {
        "id": "image-r2",
        "text": "Demo caption: A bowl of Indian lentil curry with herbs.",
        "metadata": {"restaurant_id": "r2", "cuisine": "Indian", "kind": "caption"},
    },
    {
        "id": "image-r3",
        "text": "Demo caption: Mexican fish tacos with fresh salsa.",
        "metadata": {"restaurant_id": "r3", "cuisine": "Mexican", "kind": "caption"},
    },
]
