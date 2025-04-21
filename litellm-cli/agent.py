#!/usr/bin/env python3

# /// script
# dependencies = [
#   "litellm>=1.66.3",
#   "rich>=14.0.0",
# ]
# ///

import argparse
import asyncio
import sys
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from litellm import completion
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

load_dotenv()

console = Console()

DEFAULT_MODEL_KEY = "openai/gpt-4.1-nano"
COMMAND_EXIT = "/exit"
COMMAND_MODELS = "/models"
COMMAND_SWITCH_PREFIX = "/model "

MODEL_REGISTRY: Dict[str, Dict[str, Dict[str, int]]] = {
    "openai": {
        "gpt-4.1": {"max_tokens": 1047576},
        "gpt-4.1-mini": {"max_tokens": 1047576},
        "gpt-4.1-nano": {"max_tokens": 1047576},
    },
    "anthropic": {"claude-3.7-sonnet": {"max_tokens": 200000}},
}

ChatHistory = List[Dict[str, str]]


def get_model_string(model_key: str) -> Optional[str]:
    """Return a LiteLLM‑compatible model identifier.

    Args:
        model_key: A string in the form ``<provider>/<model_name>``.

    Returns:
        The transformed model string accepted by LiteLLM or ``None`` if the
        input is invalid.
    """
    try:
        provider, model_name = model_key.split("/", 1)
    except ValueError:
        return None

    if provider not in MODEL_REGISTRY or model_name not in MODEL_REGISTRY[provider]:
        return None

    return model_name if provider == "openai" else model_key


async def stream_completion(
    prompt: str, model: str, history: ChatHistory
) -> ChatHistory:
    """Request a streamed completion and update the chat history.

    Args:
        prompt: The user input.
        model: The LiteLLM model identifier.
        history: The running chat history.

    Returns:
        The updated chat history including the assistant response.
    """
    messages = history + [{"role": "user", "content": prompt}]

    try:
        response_stream = completion(model=model, messages=messages, stream=True)
    except Exception as exc:
        console.print(f"[bold red]LiteLLM error:[/bold red] {exc}")
        return history

    response_content = ""
    with Live(
        "", refresh_per_second=15, console=console, vertical_overflow="visible"
    ) as live:
        async for chunk in response_stream:
            token = (
                chunk.choices[0].delta.content
                if chunk and chunk.choices and chunk.choices[0].delta
                else ""
            )
            if token:
                response_content += token
                live.update(Markdown(response_content))

    if response_content:
        messages.append({"role": "assistant", "content": response_content})

    return messages


def _handle_command(user_input: str, current_key: str) -> Tuple[Optional[str], bool]:
    """Handle special slash commands.

    Args:
        user_input: Raw input from the terminal.
        current_key: The model key currently in use.

    Returns:
        A tuple ``(new_model_key, should_exit)``. ``new_model_key`` is ``None``
        when no change is requested. ``should_exit`` is ``True`` when the user
        requested to terminate the session.
    """
    if user_input.lower() == COMMAND_EXIT:
        return None, True

    if user_input.lower() == COMMAND_MODELS:
        list_available_models()
        return None, False

    if user_input.lower().startswith(COMMAND_SWITCH_PREFIX):
        new_key = user_input[len(COMMAND_SWITCH_PREFIX) :].strip()
        if get_model_string(new_key):
            console.print(
                f"[green]Switched model to:[/green] [magenta]{new_key.split('/')[-1]}"
                f"[/magenta] (Key: [cyan]{new_key}[/cyan])\n"
            )
            return new_key, False
        console.print(
            f"[bold red]Invalid model key:[/bold red] {new_key}. Use /models."
        )
        return None, False

    return None, False


async def interactive_chat(initial_key: str) -> int:
    """Run an interactive chat session.

    Args:
        initial_key: The initial model key in ``<provider>/<model>`` notation.

    Returns:
        A process exit code suitable for ``sys.exit``.
    """
    history: ChatHistory = []
    current_key = initial_key

    while True:
        try:
            display_name = current_key.split("/")[-1]
            console.print(
                f"[cyan]({display_name})[/cyan] [bold green]You:[/bold green] ",
                end="",
                highlight=False,
            )
            user_input = input().strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Exiting...[/dim]")
            return 0

        if not user_input:
            continue

        new_key, should_exit = _handle_command(user_input, current_key)
        if should_exit:
            return 0
        if new_key is not None:
            current_key = new_key
            continue

        model_str = get_model_string(current_key)
        if model_str is None:
            console.print(f"[bold red]Invalid model key:[/bold red] {current_key}")
            continue

        history = await stream_completion(user_input, model_str, history)
        console.print()


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command‑line arguments.

    Args:
        args: Raw command‑line arguments (mainly for testing).

    Returns:
        A populated :class:`argparse.Namespace` instance.
    """
    parser = argparse.ArgumentParser(
        prog="litellm-cli",
        description=(
            "[bold]LiteLLM CLI Tool[/bold]\n\n"
            "Available models can be listed with --list-models.\n"
            "Switch models in interactive mode using /model <provider/model_name>.\n\n"
            "Special commands:\n"
            "* [cyan]/exit[/cyan] - Exit the interactive mode\n"
            "* [cyan]/models[/cyan] - List available models\n"
            "* [cyan]/model <key>[/cyan] - Switch to a different model"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "prompt", nargs="?", help="AI prompt. If omitted, starts interactive mode."
    )
    parser.add_argument(
        "-m",
        "--model",
        default=DEFAULT_MODEL_KEY,
        help=(
            "Model key (e.g., 'openai/gpt-4.1', 'anthropic/claude-3.7-sonnet'). "
            f"Default: {DEFAULT_MODEL_KEY}"
        ),
    )
    parser.add_argument(
        "--version", action="store_true", help="Show program version and exit"
    )
    parser.add_argument(
        "--list-models", action="store_true", help="List available models and exit"
    )
    return parser.parse_args(args)


def list_available_models() -> None:
    """Display supported model keys."""
    console.print("[bold green]Available Models:[/bold green]")
    for provider, models in MODEL_REGISTRY.items():
        console.print(f"  [magenta]{provider}[/magenta]:")
        for name in models:
            console.print(f"    - [cyan]{provider}/{name}[/cyan]")


def main(args: Optional[List[str]] = None) -> int:
    """Program entry‑point.

    Args:
        args: Raw argument list provided to the executable. ``None`` defaults to
            ``sys.argv``.

    Returns:
        Zero on success, non‑zero on failure.
    """
    parsed = parse_arguments(args)

    if parsed.version:
        console.print("[green]LiteLLM CLI v0.1.0[/green]")
        return 0

    if parsed.list_models:
        list_available_models()
        return 0

    if get_model_string(parsed.model) is None:
        console.print(f"[bold red]Invalid model key:[/bold red] {parsed.model}")
        console.print("Use --list-models to see available models.")
        return 1

    display_name = parsed.model.split("/")[-1]
    console.print(
        f"[green]Using model:[/green] [magenta]{display_name}[/magenta] "
        f"(Key: [cyan]{parsed.model}[/cyan])",
        highlight=False,
    )

    if parsed.prompt is not None:
        try:
            asyncio.run(
                stream_completion(
                    parsed.prompt, get_model_string(parsed.model) or "", []
                )
            )
        except KeyboardInterrupt:
            console.print("[dim]Interrupted[/dim]")
        return 0

    console.print(
        "Entering interactive mode. Type /exit to quit, /models to list models,",
        highlight=False,
    )
    try:
        return asyncio.run(interactive_chat(parsed.model))
    except KeyboardInterrupt:
        console.print("[dim]Interrupted[/dim]")
        return 0


if __name__ == "__main__":
    sys.exit(main())
