"""Explicitly local stand-ins for LLM and vision-LLM lab calls."""

from __future__ import annotations

import json
import re
from typing import Any


class DemoLLM:
    """Deterministic adapter used so examples run without API keys."""

    def __init__(self) -> None:
        self.repair_calls = 0

    def restaurant_json(self, paragraph: str) -> str:
        name_match = re.search(
            r"^([A-Z][A-Za-z ]+?)\s+is\s+(?:a|an)\s+", paragraph
        )
        cuisine_match = re.search(
            r"\b(Peruvian|Indian|Mexican|Italian|Japanese)\b", paragraph, re.I
        )
        city_match = re.search(r"\bin\s+([A-Z][A-Za-z-]*)", paragraph)
        name = name_match.group(1).strip() if name_match else "Unknown Restaurant"
        cuisine = cuisine_match.group(1).title() if cuisine_match else "Unknown"
        city = city_match.group(1).strip() if city_match else "Unknown"
        return json.dumps(
            {
                "name": name,
                "cuisine": cuisine,
                "city": city,
                "description": paragraph,
            },
            ensure_ascii=False,
        )

    def initial_new_restaurant_response(self, paragraph: str) -> str:
        """Return one malformed first response to exercise the repair loop."""
        return self.restaurant_json(paragraph)[:-1]

    def repair_restaurant_json(self, paragraph: str, invalid_output: str) -> str:
        if not invalid_output:
            raise ValueError("The invalid output must be provided for repair.")
        self.repair_calls += 1
        return self.restaurant_json(paragraph)

    def caption_image(self, image_uri: str) -> str:
        captions = {
            "demo://lomo-saltado":
                "Demo caption: stir-fried beef with rice and vegetables.",
            "demo://lentil-curry":
                "Demo caption: lentil curry garnished with fresh herbs.",
            "demo://fish-tacos":
                "Demo caption: fish tacos topped with salsa and greens.",
        }
        try:
            return captions[image_uri]
        except KeyError as error:
            raise ValueError(f"No demo caption is configured for {image_uri!r}.") from error

    def respond(self, query: str, restaurants: list[dict[str, Any]]) -> str:
        normalized_query = query.casefold()
        matches = [
            restaurant
            for restaurant in restaurants
            if any(
                term in normalized_query
                for term in (
                    restaurant["cuisine"].casefold(),
                    restaurant["city"].casefold(),
                    restaurant["name"].casefold(),
                    restaurant["description"].casefold(),
                )
            )
        ]
        if "vegetarian" in normalized_query or "vegan" in normalized_query:
            matches = [restaurant for restaurant in matches if restaurant["vegetarian"]]
        if not matches:
            matches = restaurants[:2]
        names = ", ".join(restaurant["name"] for restaurant in matches[:2])
        return f"Demo response: based on the local sample data, consider {names}."
