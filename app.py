"""Gradio interface for The Unofficial Guide (Milestone 5).

A web UI: type a K-pop history question, get a grounded answer. The example
questions sit in a left sidebar, the title is centered, and a TWICE photo
(assets/twice.jpg, if present) is used as the page background.

    python app.py        # then open http://localhost:7860
"""

import base64
import mimetypes
from pathlib import Path

import gradio as gr

from generate import ask

ASSETS = Path(__file__).parent / "assets"

EXAMPLES = [
    "Who is the maknae of aespa and what is her nationality?",
    "When did 2NE1 disband and which member left before that?",
    "What individual agencies did the BLACKPINK members set up?",
    "Which girl groups are under YG Entertainment?",
    "When did S.E.S disband?",
]


def handle_query(question: str):
    question = (question or "").strip()

    if not question:
        return "Please enter a question.", ""

    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"]) or "—"

    return result["answer"], sources


def _background() -> str:
    """Return a CSS background value.

    Uses a 'twice.*' image in assets/ as a data URI, matched case-insensitively.
    Falls back to a gradient if no matching image exists.
    """
    if ASSETS.is_dir():
        for path in sorted(ASSETS.iterdir()):
            if (
                path.stem.lower() == "twice"
                and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
            ):
                mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
                b64 = base64.b64encode(path.read_bytes()).decode()
                return f"url('data:{mime};base64,{b64}') center / cover fixed no-repeat"

    return "linear-gradient(135deg, #ff9ec7 0%, #a18cd1 100%)"


CSS = f"""
html, body, .gradio-container {{
    min-height: 100vh;
}}

.gradio-container {{
    background: {_background()};
    background-color: #f5f5f5;
}}

/* Soft overlay so the background image is less distracting */
.gradio-container::before {{
    content: "";
    position: fixed;
    inset: 0;
    background: rgba(255, 255, 255, 0.30);
    pointer-events: none;
    z-index: 0;
}}

.gradio-container > * {{
    position: relative;
    z-index: 1;
}}

/* Centers the whole app section */
#page {{
    width: min(1400px, calc(100vw - 64px));
    margin: 0 auto !important;
    padding-top: 22px;
}}

#content-row {{
    width: 100%;
    margin: 0 auto !important;
    gap: 18px;
}}

/* Readable title area */
#title {{
    text-align: center;
    background: rgba(0, 0, 0, 0.62);
    color: white;
    border-radius: 16px;
    padding: 18px 24px;
    margin: 0 auto 28px auto;
    max-width: 760px;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.22);
}}

#title h1 {{
    margin-bottom: 8px;
    color: white;
}}

#title p {{
    color: white;
    margin-bottom: 0;
}}

/* Light panels */
#sidebar, #main {{
    background: rgba(255, 255, 255, 0.94) !important;
    border-radius: 16px;
    padding: 18px;
    color: #111 !important;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.18);
}}

/* Make labels readable */
#sidebar label,
#main label,
#sidebar .label-wrap,
#main .label-wrap,
#sidebar span,
#main span {{
    color: #111 !important;
}}

#sidebar h3 {{
    color: #111 !important;
    margin-top: 0;
}}

/* Force Gradio examples to stack vertically in Chrome */
#sidebar .samples,
#sidebar .examples,
#sidebar .dataset,
#sidebar .table-wrap {{
    width: 100% !important;
}}

#sidebar table {{
    width: 100% !important;
    display: block !important;
}}

#sidebar tbody {{
    display: block !important;
    width: 100% !important;
}}

#sidebar tr {{
    display: block !important;
    width: 100% !important;
    margin-bottom: 8px !important;
}}

#sidebar td {{
    display: block !important;
    width: 100% !important;
    padding: 0 !important;
}}

#sidebar button {{
    width: 100% !important;
    display: block !important;
    background: rgba(255, 255, 255, 0.98) !important;
    color: #111 !important;
    border: 1px solid #999 !important;
    border-radius: 8px !important;
    text-align: left !important;
    white-space: normal !important;
    line-height: 1.35 !important;
    padding: 8px 10px !important;
}}

#sidebar button:hover {{
    background: #f0f0f0 !important;
}}

/* Black boxes with white text */
.darkbox textarea,
.darkbox input {{
    background: #000 !important;
    color: #fff !important;
    border: 1px solid #444 !important;
}}

.darkbox textarea::placeholder,
.darkbox input::placeholder {{
    color: #aaa !important;
}}

#main button {{
    margin-top: 8px;
    margin-bottom: 12px;
}}

/* Better mobile behavior */
@media screen and (max-width: 900px) {{
    #page {{
        width: calc(100vw - 24px);
        padding-top: 12px;
    }}

    #title {{
        margin-left: 0;
        margin-right: 0;
    }}

    #sidebar, #main {{
        margin-left: 0;
        margin-right: 0;
    }}
}}
"""


with gr.Blocks(title="The Unofficial Guide — K-pop") as demo:
    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. Who is the maknae of aespa?",
        elem_classes=["darkbox"],
        render=False,
    )

    answer = gr.Textbox(
        label="Answer",
        lines=10,
        elem_classes=["darkbox"],
        interactive=False,
        render=False,
    )

    sources = gr.Textbox(
        label="Retrieved from",
        lines=4,
        elem_classes=["darkbox"],
        interactive=False,
        render=False,
    )

    with gr.Column(elem_id="page"):
        gr.Markdown(
            "# The Unofficial Guide — K-pop Idol Groups\n"
            "Answers come **only** from the indexed profile documents.",
            elem_id="title",
        )

        with gr.Row(elem_id="content-row"):
            with gr.Column(scale=2, elem_id="sidebar"):
                gr.Markdown("### Example questions")
                gr.Examples(
                    examples=EXAMPLES,
                    inputs=inp,
                    label="",
                )

            with gr.Column(scale=3, elem_id="main"):
                inp.render()
                btn = gr.Button("Ask", variant="primary")
                answer.render()
                sources.render()

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)

    style_path = ASSETS / "_style.css"
    style_path.write_text(CSS, encoding="utf-8")

    demo.launch(css_paths=[str(style_path)])