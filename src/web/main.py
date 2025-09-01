"""
Web interface main entry point for Yahoo Finance CSV converter.
"""

import logging
from typing import Any, Optional

import gradio as gr

from src.web.converters import schwab_converter

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create tabbed interface with available converters
app = gr.TabbedInterface(
    [schwab_converter],
    ["Schwab Converter"],
    title="Yahoo Finance CSV Converter",
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="gray",
    ),
)


def launch(
    share: bool = True,
    server_name: Optional[str] = None,
    server_port: Optional[int] = None,
) -> Any:
    """
    Launch the web interface.

    Args:
        share: Whether to create a publicly shareable link
        server_name: Server name to use (defaults to gradio defaults)
        server_port: Server port to use (defaults to gradio defaults)

    Returns:
        Gradio app instance
    """
    return app.launch(share=share, server_name=server_name, server_port=server_port)


if __name__ == "__main__":
    # When run directly, launch the app
    launch()
