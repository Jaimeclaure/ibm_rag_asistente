"""Generate clearly labeled, illustrative PNG evidence cards for the local demo."""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent
IMAGE_SIZE = (1920, 1080)
BACKGROUND = "#111827"
PANEL = "#1f2937"
PANEL_HEADER = "#374151"
TEXT = "#e5e7eb"
MUTED = "#9ca3af"
GREEN = "#86efac"
AMBER = "#fbbf24"
BLUE = "#93c5fd"


@dataclass(frozen=True)
class CaptureSpec:
    filename: str
    title: str
    source_file: str
    symbols: tuple[str, ...]
    command: tuple[str, ...]
    output_selector: Callable[[str], str]
    ui_preview: bool = False


def _section(output: str, start: str, end: str | None = None) -> str:
    lines = output.splitlines()
    start_index = next(
        (index for index, line in enumerate(lines) if line.startswith(start)),
        None,
    )
    if start_index is None:
        raise RuntimeError(f"Expected output section {start!r} was not produced.")
    if end is None:
        selected = lines[start_index:]
    else:
        end_index = next(
            (
                index
                for index in range(start_index + 1, len(lines))
                if lines[index].startswith(end)
            ),
            len(lines),
        )
        selected = lines[start_index:end_index]
    return "\n".join(selected)


def _vector_index_output(output: str) -> str:
    return _section(output, "Created Chroma collection:", "Retrieval query:")


def _retrieval_output(output: str) -> str:
    return _section(
        output,
        "Retrieval query:",
        "Similarity Retrieval with Metadata Filtering COMPLETE",
    ) + "\nSimilarity Retrieval with Metadata Filtering COMPLETE"


def _fusion_output(output: str) -> str:
    return _section(output, "Multimodal fusion query:")


def _module3_section(output: str, start: str, end: str | None = None) -> str:
    return _section(output, start, end)


def _mcp_search_output(output: str) -> str:
    lines = output.splitlines()
    try:
        start = lines.index("Successful search query result:")
        end = next(
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("Configured project root verified:")
        )
    except (ValueError, StopIteration) as error:
        raise RuntimeError("The MCP demo did not produce the expected JSON search result.") from error
    return "\n".join(lines[start:end])


def _mcp_client_output(output: str) -> str:
    lines = output.splitlines()
    selected = [
        line
        for line in lines
        if line.startswith(
            (
                "Operational tools verified:",
                "Available resources:",
                "Configured project root verified:",
            )
        )
    ]
    if len(selected) != 3:
        raise RuntimeError("The MCP demo did not verify tools, resources, and project roots.")
    return "\n".join(selected)


def _chatbot_output(output: str) -> str:
    if not output.strip():
        raise RuntimeError("The chatbot demo did not produce a response.")
    return output.strip()


CAPTURES = (
    CaptureSpec(
        "M1L1_structure_for_loop.png",
        "Q1 | Generate and validate restaurant JSON",
        "restaurant_project/module1.py",
        ("generate_and_validate_restaurants",),
        ("-m", "restaurant_project.module1"),
        lambda output: _section(
            output,
            "Q1 - Generate and validate restaurant JSON",
            "Q2 - Caption",
        ),
    ),
    CaptureSpec(
        "M1L2_caption_all_recipes.png",
        "Q2 | Caption recipe images",
        "restaurant_project/module1.py",
        ("caption_all_recipes",),
        ("-m", "restaurant_project.module1"),
        lambda output: _section(
            output,
            "Q2 - Caption",
            "Q3 - Parse",
        ),
    ),
    CaptureSpec(
        "M1L3_new_data_entry_process.png",
        "Q3 | Validate and repair JSON",
        "restaurant_project/module1.py",
        ("process_new_restaurant",),
        ("-m", "restaurant_project.module1"),
        lambda output: _section(output, "Q3 - Parse"),
    ),
    CaptureSpec(
        "M2L1_multimodal_vector_index.png",
        "Q4 | Build the multimodal vector index",
        "restaurant_project/vector_index.py",
        ("build_multimodal_vector_index",),
        ("-m", "restaurant_project.vector_index"),
        _vector_index_output,
    ),
    CaptureSpec(
        "M2L2_similarity_retrieval.png",
        "Q5 | Similarity retrieval with metadata filtering",
        "restaurant_project/vector_index.py",
        ("run_similarity_retrieval",),
        ("-m", "restaurant_project.vector_index"),
        _retrieval_output,
    ),
    CaptureSpec(
        "M2L3_multimodal_fusion_results.png",
        "Q6 | Multimodal fusion ranking",
        "restaurant_project/vector_index.py",
        ("run_fusion_demo",),
        ("-m", "restaurant_project.vector_index"),
        _fusion_output,
    ),
    CaptureSpec(
        "M3L1_food_style_expert_goal.png",
        "Q7 | Food Style Expert configuration",
        "restaurant_project/module3.py",
        ("AgentConfiguration", "food_style_expert"),
        ("-m", "restaurant_project.module3"),
        lambda output: _module3_section(
            output,
            "Q7 - Food Style Expert configuration",
            "Q8 - Analyze",
        ),
    ),
    CaptureSpec(
        "M3L2_node_analyze_styles.png",
        "Q8 | Analyze styles node",
        "restaurant_project/module3.py",
        ("node_analyze_styles",),
        ("-m", "restaurant_project.module3"),
        lambda output: _module3_section(
            output,
            "Q8 - Analyze",
            "Q9 - Test",
        ),
    ),
    CaptureSpec(
        "M3L3_preference_extraction_test.png",
        "Q9 | Test preference extraction",
        "restaurant_project/module3.py",
        ("extract_preferences", "test_extract_preferences"),
        ("-m", "restaurant_project.module3"),
        lambda output: _module3_section(output, "Q9 - Test"),
    ),
    CaptureSpec(
        "M4L1_Configure_Tools_Data_MCP_Server.png",
        "Q10 | MCP server search result",
        "restaurant_project/mcp_server.py",
        ("search_restaurants",),
        ("-m", "restaurant_project.mcp_client"),
        _mcp_search_output,
    ),
    CaptureSpec(
        "M4L2_Build_Test_MCP_Client.png",
        "Q11 | Verify MCP client tools, resources, and root",
        "restaurant_project/mcp_client.py",
        ("main",),
        ("-m", "restaurant_project.mcp_client"),
        _mcp_client_output,
    ),
    CaptureSpec(
        "M4L3_Design_LLM_MCP_Host.png",
        "Q12 | Restaurant chatbot interface",
        "restaurant_project/chatbot.py",
        ("respond", "create_demo"),
        (
            "-c",
            (
                "from restaurant_project.chatbot import respond; "
                "history, _ = respond('Find vegetarian food in Boston', []); "
                "print(history[-2]['content']); print(history[-1]['content'])"
            ),
        ),
        _chatbot_output,
        ui_preview=True,
    ),
)


def _font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    font_candidates = (
        (r"C:\Windows\Fonts\consolab.ttf", r"C:\Windows\Fonts\consola.ttf")
        if mono and bold
        else (r"C:\Windows\Fonts\consola.ttf",)
        if mono
        else (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\segoeui.ttf")
        if bold
        else (r"C:\Windows\Fonts\segoeui.ttf",)
    )
    for candidate in font_candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def _source_excerpt(spec: CaptureSpec) -> list[tuple[int, str]]:
    source_path = PROJECT_ROOT / spec.source_file
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(source_path))
    lines = source.splitlines()
    excerpts: list[tuple[int, str]] = []

    for symbol in spec.symbols:
        node = next(
            (
                item
                for item in tree.body
                if getattr(item, "name", None) == symbol
                or (
                    isinstance(item, ast.Assign)
                    and any(
                        isinstance(target, ast.Name) and target.id == symbol
                        for target in item.targets
                    )
                )
            ),
            None,
        )
        if node is None or node.end_lineno is None:
            raise RuntimeError(f"Could not locate {symbol!r} in {spec.source_file}.")
        start = node.lineno
        if excerpts:
            excerpts.append((0, ""))
        excerpts.extend(
            (line_number, lines[line_number - 1])
            for line_number in range(start, node.end_lineno + 1)
        )
    return excerpts


def _run_demo_command(
    spec: CaptureSpec, cache: dict[tuple[str, ...], str]
) -> str:
    command = (sys.executable, *spec.command)
    if command not in cache:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                f"Demo command failed ({result.returncode}): {' '.join(command)}\n"
                f"{result.stderr.strip()}"
            )
        cache[command] = result.stdout
    return spec.output_selector(cache[command])


def _wrap_pixels(
    text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw
) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _draw_code_panel(
    draw: ImageDraw.ImageDraw,
    code_font: ImageFont.FreeTypeFont,
    excerpt: list[tuple[int, str]],
    bounds: tuple[int, int, int, int],
) -> None:
    left, top, right, bottom = bounds
    draw.rounded_rectangle(bounds, radius=16, fill=PANEL)
    draw.rounded_rectangle((left, top, right, top + 50), radius=16, fill=PANEL_HEADER)
    draw.rectangle((left, top + 30, right, top + 50), fill=PANEL_HEADER)
    draw.text((left + 20, top + 12), "CODIGO DE LA DEMO", font=_font(19, bold=True), fill=BLUE)

    line_height = 22
    max_lines = max(1, (bottom - top - 75) // line_height)
    for row, (line_number, content) in enumerate(excerpt[:max_lines]):
        y = top + 66 + row * line_height
        number = f"{line_number:>3}" if line_number else "   "
        draw.text((left + 16, y), number, font=code_font, fill=MUTED)
        draw.text((left + 66, y), content[:105], font=code_font, fill=TEXT)
    if len(excerpt) > max_lines:
        draw.text(
            (left + 18, bottom - 30),
            "...fragmento recortado; consulta el archivo fuente.",
            font=_font(16),
            fill=AMBER,
        )


def _draw_output_panel(
    draw: ImageDraw.ImageDraw,
    output_font: ImageFont.FreeTypeFont,
    output: str,
    bounds: tuple[int, int, int, int],
) -> None:
    left, top, right, bottom = bounds
    draw.rounded_rectangle(bounds, radius=16, fill="#030712")
    draw.rounded_rectangle((left, top, right, top + 50), radius=16, fill=PANEL_HEADER)
    draw.rectangle((left, top + 30, right, top + 50), fill=PANEL_HEADER)
    draw.text((left + 20, top + 12), "SALIDA REAL DE LA DEMO", font=_font(19, bold=True), fill=GREEN)

    line_height = 22
    max_width = right - left - 36
    wrapped: list[str] = []
    for line in output.splitlines():
        wrapped.extend(_wrap_pixels(line, output_font, max_width, draw))
    max_lines = max(1, (bottom - top - 78) // line_height)
    for row, line in enumerate(wrapped[:max_lines]):
        draw.text((left + 18, top + 64 + row * line_height), line, font=output_font, fill=TEXT)
    if len(wrapped) > max_lines:
        draw.text(
            (left + 18, bottom - 30),
            "...salida recortada.",
            font=_font(16),
            fill=AMBER,
        )


def _draw_ui_preview(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int]) -> None:
    left, top, right, bottom = bounds
    draw.rounded_rectangle(bounds, radius=18, fill="#f8fafc")
    draw.text((left + 28, top + 26), "Restaurant RAG Assistant", font=_font(27, bold=True), fill="#0f172a")
    draw.text(
        (left + 28, top + 70),
        "Recomendaciones con datos locales de ejemplo",
        font=_font(17),
        fill="#475569",
    )
    draw.rounded_rectangle(
        (left + 22, top + 120, right - 22, bottom - 88),
        radius=14,
        fill="#e2e8f0",
    )
    draw.rounded_rectangle(
        (left + 44, top + 146, right - 90, top + 206),
        radius=14,
        fill="#ffffff",
    )
    draw.text(
        (left + 60, top + 164),
        "Find vegetarian food in Boston",
        font=_font(17),
        fill="#0f172a",
    )
    draw.rounded_rectangle(
        (left + 112, top + 224, right - 44, top + 300),
        radius=14,
        fill="#dbeafe",
    )
    draw.text(
        (left + 130, top + 241),
        "Demo response: consider Green Garden.",
        font=_font(16),
        fill="#0f172a",
    )

    button_y = bottom - 154
    button_labels = (
        "Vegetarian food",
        "Peruvian cuisine",
        "Seafood options",
    )
    button_width = (right - left - 64) // 3
    for index, label in enumerate(button_labels):
        x = left + 22 + index * (button_width + 10)
        draw.rounded_rectangle(
            (x, button_y, x + button_width, button_y + 38),
            radius=12,
            fill="#e0e7ff",
        )
        draw.text((x + 8, button_y + 10), label, font=_font(13), fill="#1e3a8a")

    input_y = bottom - 102
    draw.rounded_rectangle(
        (left + 22, input_y, right - 108, input_y + 42),
        radius=10,
        outline="#94a3b8",
        width=2,
        fill="#ffffff",
    )
    draw.text((left + 34, input_y + 10), "Escribe tu consulta...", font=_font(15), fill="#64748b")
    draw.rounded_rectangle(
        (right - 98, input_y, right - 22, input_y + 42),
        radius=10,
        fill="#2563eb",
    )
    draw.text((right - 83, input_y + 10), "Send", font=_font(15, bold=True), fill="#ffffff")
    draw.text(
        (left + 22, bottom - 48),
        "Built with Gradio | Vista ilustrativa, no es una captura del navegador",
        font=_font(14),
        fill="#475569",
    )


def _render_capture(
    spec: CaptureSpec,
    excerpt: list[tuple[int, str]],
    output: str,
    destination: Path,
) -> None:
    image = Image.new("RGB", IMAGE_SIZE, BACKGROUND)
    draw = ImageDraw.Draw(image)
    title_font = _font(32, bold=True)
    body_font = _font(17)
    code_font = _font(15, mono=True)
    output_font = _font(16, mono=True)

    draw.text((46, 34), spec.title, font=title_font, fill=TEXT)
    draw.rounded_rectangle((1425, 35, 1870, 78), radius=14, fill="#78350f")
    draw.text((1444, 47), "DEMO LOCAL - NO OFICIAL", font=_font(17, bold=True), fill="#fef3c7")
    draw.text(
        (48, 88),
        f"Fuente: {spec.source_file}  |  Evidencia ilustrativa generada desde el proyecto local",
        font=body_font,
        fill=MUTED,
    )

    if spec.ui_preview:
        _draw_code_panel(draw, code_font, excerpt, (48, 140, 906, 968))
        _draw_ui_preview(draw, (936, 140, 1872, 968))
    else:
        _draw_code_panel(draw, code_font, excerpt, (48, 140, 1030, 968))
        _draw_output_panel(draw, output_font, output, (1060, 140, 1872, 968))

    draw.text(
        (48, 1018),
        "No sustituye las capturas requeridas de los laboratorios originales de IBM.",
        font=_font(17, bold=True),
        fill=AMBER,
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, format="PNG", optimize=True)


def generate_captures(output_dir: Path) -> list[Path]:
    output_cache: dict[tuple[str, ...], str] = {}
    generated: list[Path] = []
    for spec in CAPTURES:
        excerpt = _source_excerpt(spec)
        output = _run_demo_command(spec, output_cache)
        destination = output_dir / spec.filename
        _render_capture(spec, excerpt, output, destination)
        generated.append(destination)
        print(f"Generated: {destination}")
    return generated


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate 12 explicitly labeled illustrative screenshots for the local demo."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "capturas_demo",
        help="Folder where the PNG files are written (default: capturas_demo).",
    )
    args = parser.parse_args()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir
    generated = generate_captures(output_dir)
    print(f"\nGenerated {len(generated)} illustrative PNG files in: {output_dir}")
    print("All files are labeled as local demo material, not official lab evidence.")


if __name__ == "__main__":
    main()
