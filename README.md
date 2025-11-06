# Computer Use Agent

macOS desktop automation using Gemini Computer Use API.

## Setup

```bash
# Install dependencies
uv sync

# Set API key
export GEMINI_API_KEY='your-api-key'
```

## Usage

After installation, use the `computer-agent` command:

### Slack Automation

```bash
# Search with Slack query language
computer-agent --app slack "Find messages from:@john in:#engineering after:2025-01-01"

# Summarize today's messages
computer-agent --app slack "Summarize today's messages in #general"
```

### Generic macOS

```bash
# Finder
computer-agent --app finder "Create folder 'Projects' on Desktop"

# Any app
computer-agent --app chrome "Search for Python tutorials"
```

### Alternative: Run as module

```bash
python -m computer_use_agent.cli --app slack "your goal"
```

### Options

```bash
--app APP                 # App name (default: Desktop Application)
--max-iterations N        # Max steps (default: 20)
--thinking                # Enable debug mode
--no-safety               # Disable safety checks (not recommended)
--quiet                   # Less output
```

## Architecture

```
src/computer_use_agent/
├── config/          # Settings & prompts
├── actions/         # Desktop automation
├── utils/           # Retry & response handling
├── agent.py         # Core orchestrator
└── cli.py           # CLI interface
