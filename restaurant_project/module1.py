"""Demonstrations corresponding to Module 1 tasks Q1–Q3."""

from __future__ import annotations

import json
from typing import Any

from restaurant_project.data import RECIPES, RESTAURANT_PARAGRAPHS
from restaurant_project.llm import DemoLLM

REQUIRED_FIELDS = {"name", "cuisine", "city", "description"}


def validate_restaurant_json(output: str) -> dict[str, Any]:
    try:
        restaurant = json.loads(output)
    except json.JSONDecodeError as error:
        raise ValueError(f"LLM response is not valid JSON: {error}") from error
    if not isinstance(restaurant, dict) or not REQUIRED_FIELDS.issubset(restaurant):
        raise ValueError(f"Restaurant JSON must contain {sorted(REQUIRED_FIELDS)}.")
    if not all(isinstance(restaurant[field], str) for field in REQUIRED_FIELDS):
        raise ValueError("All required restaurant fields must be strings.")
    return restaurant


def generate_and_validate_restaurants(
    paragraphs: list[str], llm: DemoLLM
) -> list[dict[str, Any]]:
    restaurants = []
    for paragraph in paragraphs:
        generated_json = llm.restaurant_json(paragraph)
        restaurants.append(validate_restaurant_json(generated_json))
    return restaurants


def caption_all_recipes(
    recipes: list[dict[str, str]], vision_llm: DemoLLM
) -> list[dict[str, str]]:
    captioned_recipes = []
    for recipe in recipes:
        caption = vision_llm.caption_image(recipe["image_uri"])
        captioned_recipes.append({**recipe, "caption": caption})
    return captioned_recipes


def process_new_restaurant(
    paragraph: str, llm: DemoLLM, max_repairs: int = 3
) -> dict[str, Any]:
    if max_repairs < 0:
        raise ValueError("max_repairs cannot be negative.")
    response = llm.initial_new_restaurant_response(paragraph)
    for attempt in range(max_repairs + 1):
        try:
            return validate_restaurant_json(response)
        except ValueError:
            if attempt == max_repairs:
                raise
            print(f"Invalid JSON; attempting repair {attempt + 1}/{max_repairs}...")
            response = llm.repair_restaurant_json(paragraph, response)
    raise RuntimeError("Unreachable JSON repair state.")


def main() -> None:
    llm = DemoLLM()

    print("Q1 - Generate and validate restaurant JSON")
    restaurants = generate_and_validate_restaurants(RESTAURANT_PARAGRAPHS, llm)
    for restaurant in restaurants:
        print(json.dumps(restaurant, ensure_ascii=False))

    print("\nQ2 - Caption recipe images (deterministic demo captions)")
    for recipe in caption_all_recipes(RECIPES, llm):
        print(f"{recipe['name']}: {recipe['caption']}")

    print("\nQ3 - Parse a new restaurant paragraph with validation and repair")
    new_restaurant = process_new_restaurant(
        "Sunrise Table is an Indian restaurant in Boston with fresh dosa.",
        llm,
    )
    print(json.dumps(new_restaurant, ensure_ascii=False))


if __name__ == "__main__":
    main()
