"""Agent configuration and preference extraction demonstrations for Q7–Q9."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from restaurant_project.data import RESTAURANTS
from restaurant_project.llm import DemoLLM


@dataclass(frozen=True)
class AgentConfiguration:
    role: str
    goal: str
    backstory: str


food_style_expert = AgentConfiguration(
    role="Food Style Expert",
    goal="Match restaurant recommendations to the user's cuisine, dietary, and dining-style preferences.",
    backstory=(
        "You are a thoughtful culinary guide who compares cuisines, ingredients, "
        "and dining atmospheres without inventing restaurant details."
    ),
)


def node_analyze_styles(state: dict[str, Any]) -> dict[str, Any]:
    user_message = (
        "Analyze the user's food and dining style preferences. "
        f"User request: {state['user_input']}\n"
        "Return concise cuisine, dietary, and atmosphere preferences."
    )
    analyzed_state = dict(state)
    analyzed_state["user_message"] = user_message
    analyzed_state["style_analysis"] = DemoLLM().respond(
        state["user_input"], RESTAURANTS
    )
    return analyzed_state


def extract_preferences(message: str) -> dict[str, Any]:
    normalized = message.casefold()
    cuisines = [
        cuisine
        for cuisine in ("Peruvian", "Indian", "Mexican", "Italian", "Japanese")
        if cuisine.casefold() in normalized
    ]
    return {
        "cuisines": cuisines,
        "vegetarian": bool(re.search(r"\bvegetarian|vegan\b", normalized)),
        "spicy": bool(re.search(r"\bspicy|hot\b", normalized)),
        "city": (
            "Boston"
            if "boston" in normalized
            else "Cambridge"
            if "cambridge" in normalized
            else None
        ),
    }


def test_extract_preferences() -> None:
    preferences = extract_preferences(
        "I want spicy Indian food in Boston, preferably vegetarian."
    )
    assert preferences == {
        "cuisines": ["Indian"],
        "vegetarian": True,
        "spicy": True,
        "city": "Boston",
    }
    print(f"extract_preferences test passed: {preferences}")


def main() -> None:
    print("Q7 - Food Style Expert configuration")
    print(f"Role: {food_style_expert.role}")
    print(f"Goal: {food_style_expert.goal}")
    print(f"Backstory: {food_style_expert.backstory}")

    print("\nQ8 - Analyze styles node")
    result = node_analyze_styles(
        {"user_input": "I like vegetarian Indian food in Boston."}
    )
    print(f"user_message:\n{result['user_message']}")
    print(f"style_analysis: {result['style_analysis']}")

    print("\nQ9 - Test preference extraction")
    test_extract_preferences()


if __name__ == "__main__":
    main()
