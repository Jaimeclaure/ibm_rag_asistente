from __future__ import annotations

import unittest

from restaurant_project.data import RESTAURANT_PARAGRAPHS, RESTAURANTS
from restaurant_project.llm import DemoLLM
from restaurant_project.module1 import (
    caption_all_recipes,
    generate_and_validate_restaurants,
    process_new_restaurant,
)
from restaurant_project.module3 import extract_preferences, node_analyze_styles
from restaurant_project.vector_index import VECTOR_SIZE, embed_text


class DemoTests(unittest.TestCase):
    def test_restaurant_generation_validates_each_output(self) -> None:
        restaurants = generate_and_validate_restaurants(
            RESTAURANT_PARAGRAPHS, DemoLLM()
        )
        self.assertEqual(len(restaurants), len(RESTAURANT_PARAGRAPHS))
        self.assertEqual(restaurants[0]["name"], "Andean Table")

    def test_recipe_captions_are_assigned(self) -> None:
        recipes = [{"name": "Lomo saltado", "image_uri": "demo://lomo-saltado"}]
        captioned = caption_all_recipes(recipes, DemoLLM())
        self.assertIn("caption", captioned[0])

    def test_new_restaurant_processing_returns_valid_object(self) -> None:
        llm = DemoLLM()
        restaurant = process_new_restaurant(
            "Sunrise Table is an Indian restaurant in Boston with fresh dosa.",
            llm,
        )
        self.assertEqual(restaurant["cuisine"], "Indian")
        self.assertEqual(restaurant["city"], "Boston")
        self.assertEqual(llm.repair_calls, 1)

    def test_preference_extraction(self) -> None:
        self.assertEqual(
            extract_preferences("Spicy Indian vegetarian food in Boston"),
            {
                "cuisines": ["Indian"],
                "vegetarian": True,
                "spicy": True,
                "city": "Boston",
            },
        )

    def test_style_node_constructs_user_message(self) -> None:
        result = node_analyze_styles({"user_input": "Mexican seafood"})
        self.assertIn("Mexican seafood", result["user_message"])

    def test_demo_embedding_is_reproducible(self) -> None:
        self.assertEqual(embed_text("Peruvian cuisine"), embed_text("Peruvian cuisine"))
        self.assertEqual(len(embed_text("Peruvian cuisine")), VECTOR_SIZE)


if __name__ == "__main__":
    unittest.main()
