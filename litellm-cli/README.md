# LiteLLM‑CLI – A Single‑File AI Chat Agent

> "You don't always need a complex framework – a single Python file can be enough to chat with powerful LLMs."

This project is a **proof‑of‑concept** showing how little code you really need to tap into today's large language models.  
`agent.py` is fewer than 300 lines, yet it can already:

* stream responses from GPT‑4.1 (or any model LiteLLM supports)
* switch models on the fly with a slash command
* remember conversation history (in the same terminal session)
* list available models

All of that **without** setting‑up a virtual‑environment or installing any dependencies manually – thanks to [uv](https://docs.astral.sh/uv/).

---

## Quick Start

```bash
# 1. Clone the repo (or download the single file)
$ git clone https://github.com/MarkusOdenthal/single-file-agents.git
$ cd single-file-agents/litellm-cli

# 2. Install `uv` (once per machine)
# (pick ONE of the following – pipx is recommended)
$ pipx install uv               # via pipx
# brew install astral-sh/uv/uv  # via Homebrew (macOS)
# scoop install uv              # via Scoop   (Windows)

# 3. Create your environment file
$ cp .env_example .env          # rename the example file
$ $EDITOR .env                  # paste your keys

# 4. Chat with an LLM 🚀
$ uv sync
$ uv run agent.py               # interactive mode
```

`uv` will automatically:
1. read the dependency block at the top of *agent.py*
2. create a fresh, isolated virtual‑environment
3. install the required packages (`litellm`, `rich`, and their transitive deps)
4. execute the script inside that env

The next run will be instant – the same environment is reused.

---

## Environment Variables
The script relies on standard environment variables understood by LiteLLM.
They can be defined in any way you like – the simplest is a **.env** file in the same folder:

```dotenv
OPENAI_API_KEY=sk‑...
ANTHROPIC_API_KEY=claude‑...
```

---

## Usage

```text
$ uv run agent.py [PROMPT] [options]
```

• If **PROMPT** is provided, the agent answers once and exits.  
• Without a prompt it enters **interactive chat mode**.

### Common options

| Flag | Description |
|------|-------------|
| `-m`, `--model <key>` | Default model to use (e.g. `openai/gpt-4.1`, `anthropic/claude-3.7-sonnet`). |
| `--list-models` | List the hard‑coded demo models and exit. |
| `--version` | Show programme version. |

Run `uv run agent.py --help` to see the full built‑in help.

### Slash commands (interactive mode)

| Command | Action |
|---------|--------|
| `/exit` | Quit the programme |
| `/models` | Show available model keys |
| `/model <key>` | Switch to another model mid‑conversation |

Example session:

```text
$ uv run agent.py
(openai/gpt-4.1-nano) You: hello there!
# ...streamed answer appears...
/model anthropic/claude-3.7-sonnet
(claude-3.7-sonnet) You: thanks!
```

---

## How it Works

1. The first three lines of *agent.py* contain **PEP‑723 inline metadata**:

   ```python
   # /// script
   # dependencies = [
   #   "litellm>=1.66.3",
   #   "rich>=14.0.0",
   # ]
   # ///
   ```

2. `uv run agent.py` reads that block, prepares an environment with those packages, and then runs Python.
3. `agent.py` loads your API keys via `python‑dotenv`, then uses **LiteLLM** to hit whichever provider/model you selected.
4. Streaming tokens are rendered live via the excellent **rich** library.

That's it – no `requirements.txt`, `pyproject.toml`, or Docker image in sight.  
If you ever want to freeze dependencies you can run `uv lock --script agent.py` to generate a lockfile next to the script.

---

## Supported Models
The demo ships with a minimal registry in the code:

* `openai/gpt‑4.1`, `openai/gpt‑4.1‑mini`, `openai/gpt‑4.1‑nano`
* `anthropic/claude‑3.7‑sonnet`

Feel free to edit `MODEL_REGISTRY` in *agent.py* and add any model LiteLLM supports (there are many!).

---

## Why LiteLLM?

[LiteLLM](https://github.com/BerriAI/litellm) provides a unified API layer for dozens of providers – OpenAI, Anthropic, Groq, Mistral, Fireworks AI and more.  
That means **the rest of the code never changes** when you switch hardware or models.
