# Claude Code Clone: Terminal AI Agent

A lightweight, terminal-based AI coding assistant built in Python. It implements a **ReAct (Reasoning + Acting)** agent loop that lets an LLM autonomously read files, write code, and run shell commands to fulfill a user's request.

Originally built as part of the [CodeCrafters](https://codecrafters.io) "Build Your Own Claude Code" challenge, the agent is powered by Anthropic's **Claude 3.5 Haiku** via the **OpenRouter** API.

> [!WARNING]
> This agent can execute arbitrary shell commands. Run it inside Docker (recommended) and never point it at directories you can't afford to lose. See [Safety](#safety).

## Features

- **Agentic loop:** keeps reasoning and calling tools until the prompt is fully resolved.
- **File system access:** reads existing files and writes or overwrites files with generated code.
- **Shell execution:** runs bash commands to explore directories, run tests, or execute code it just wrote.
- **Docker sandboxing:** ships with a Dockerfile so the agent runs in an isolated environment, protecting your host machine.

## How It Works

1. Your prompt is sent to the model along with the tool definitions (`Read`, `Write`, `Bash`).
2. If the model responds with a tool call, the agent executes it and appends the result to the conversation.
3. The updated conversation is sent back to the model.
4. Steps 2–3 repeat until the model replies without a tool call, which is treated as the final answer.

## Tools

| Tool    | Description                                                    |
|---------|----------------------------------------------------------------|
| `Read`  | Reads and returns the contents of a specified file.            |
| `Write` | Writes content to a specified file (creates or overwrites).    |
| `Bash`  | Executes a shell command and returns its stdout or stderr.     |

## Prerequisites

- Python 3.11+ **or** Docker
- An [OpenRouter API key](https://openrouter.ai/keys)

## Installation & Usage

### Option 1: Docker (recommended)

Because the agent can run raw bash commands, running it in a container is strongly recommended.

**1. Build the image**

```bash
docker build -t claude-sandbox .
```

**2. Run the agent with a prompt**

```bash
docker run --rm \
  -e OPENROUTER_API_KEY="your_api_key_here" \
  claude-sandbox \
  -p "Write a python script that calculates the Fibonacci sequence, then run it."
```

**3. (Optional) Persist generated files**

Mount a local folder to keep whatever the agent creates:

```bash
docker run --rm \
  -v "$(pwd)/workspace:/app/workspace" \
  -e OPENROUTER_API_KEY="your_api_key_here" \
  claude-sandbox \
  -p "Create a React component inside the workspace folder."
```

### Option 2: Local Python

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Set your API key**

```bash
export OPENROUTER_API_KEY="your_api_key_here"
```

**3. Run the script**

```bash
python main.py -p "What files are in this directory?"
```

## Configuration

| Variable             | Required | Description                     |
|----------------------|----------|---------------------------------|
| `OPENROUTER_API_KEY` | Yes      | Your OpenRouter API key.        |

| Flag | Description                          |
|------|--------------------------------------|
| `-p` | The prompt/task to give to the agent |

## Safety

The `Bash` tool gives the LLM the same power over your machine that you have in your terminal.

- Prefer Docker, and mount only the directory you want the agent to work in.
- If running locally, avoid prompts that could lead to destructive commands (e.g. deleting or overwriting important directories).
- Never commit your API key. Pass it via environment variables only.

## Acknowledgements

- [CodeCrafters](https://codecrafters.io) for the "Build Your Own Claude Code" challenge.
- [OpenRouter](https://openrouter.ai) for model access.
- [Anthropic](https://www.anthropic.com) for Claude.