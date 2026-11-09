"""Local Gradio chatbot demo corresponding to Module 4, Q12."""

from __future__ import annotations

from typing import Any

import gradio as gr

from restaurant_project.data import RESTAURANTS
from restaurant_project.llm import DemoLLM

llm = DemoLLM()
QUICK_ACTIONS = (
    "Find vegetarian food in Boston",
    "Recommend Peruvian cuisine",
    "Show seafood options",
)


def respond(message: str, history: list[dict[str, Any]] | None) -> tuple[list[dict[str, str]], str]:
    if not message.strip():
        raise gr.Error("Enter a restaurant or food preference.")
    conversation = list(history or [])
    conversation.extend(
        [
            {"role": "user", "content": message},
            {
                "role": "assistant",
                "content": llm.respond(message, RESTAURANTS),
            },
        ]
    )
    return conversation, ""


def create_demo() -> gr.Blocks:
    with gr.Blocks(title="Restaurant RAG Assistant") as demo:
        gr.Markdown("# Restaurant RAG Assistant")
        gr.Markdown(
            "Explore fictional restaurant recommendations. "
            "**Offline demo:** responses use local sample data."
        )
        chatbot = gr.Chatbot(label="Conversation", height=360)
        message = gr.Textbox(
            label="Ask for a recommendation",
            placeholder="For example: vegetarian Indian food in Boston",
        )
        submit = gr.Button("Send", variant="primary")
        with gr.Row():
            quick_buttons = [
                gr.Button(action, size="sm") for action in QUICK_ACTIONS
            ]

        submit.click(respond, inputs=[message, chatbot], outputs=[chatbot, message])
        message.submit(respond, inputs=[message, chatbot], outputs=[chatbot, message])
        for action, button in zip(QUICK_ACTIONS, quick_buttons):
            button.click(
                lambda history, prompt=action: respond(prompt, history),
                inputs=[chatbot],
                outputs=[chatbot, message],
            )
        gr.Markdown("Built with Gradio")
    return demo


def main() -> None:
    create_demo().launch(theme=gr.themes.Soft())


if __name__ == "__main__":
    main()
