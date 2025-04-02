# Strategic Advisor - AI-Powered Personal Coach

A terminal-based AI strategic advisor built with Pydantic AI that provides brutally honest feedback and actionable advice to help you grow personally and professionally.

## Features

- =� Interactive chat interface in your terminal
- >� Built with Pydantic AI for easy model switching
- =� Fast responses with output streaming
- =� Strategic advice focused on personal and professional growth
- =( Single file implementation with zero installation requirements

## Installation

No installation needed! This is a self-contained script using Python's built-in `uv` inline dependencies system.

Simply run:

```bash
uv run agent.py
```

The script will automatically install required dependencies if they're missing.

## Usage

### Basic Usage

Run the script to start an interactive chat session:

```bash
uv run agent.py
```

Or provide a prompt directly:

```bash
uv run agent.py "I need advice on my career transition"
```

### Command-Line Options

- `-m, --model` - Model to use, e.g., "openai:gpt-4o" (default)
- `-l, --list-models` - List all available models and exit
- `-t, --code-theme` - Set color theme for code blocks (dark/light/custom)
- `--no-stream` - Disable response streaming
- `--version` - Show version and exit

### Interactive Commands

During an interactive session, you can use these special commands:

- `/exit` - Exit the interactive mode
- `/markdown` - Display the raw markdown from the last response
- `/multiline` - Toggle multiline input mode

## Development

This project is designed as a single-file agent using Pydantic AI for the core AI functionality.

### Requirements

- Python 3.8+
- Dependencies (auto-installed): pydantic-ai

### Project Structure

- `agent.py` - The main script implementing both the agent and CLI
- `README.md` - Project documentation
- `specs/` - Project specifications
- `ai_docs/` - Reference implementations

## License

MIT