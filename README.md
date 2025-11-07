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

```bash
# Basic usage (goals are auto-rewritten for better results)
computer-agent --app slack "Find messages from John in engineering"

# YOLO mode (auto-approves all actions)
computer-agent --yolo-mode --app chrome "Search for AI trends and summarize"

# Skip goal rewriting
computer-agent --no-rewrite --app finder "Create folder Projects"
```

### Examples

```bash
# Slack automation
computer-agent --app slack "Summarize today's messages in #general"

# Multi-app workflow  
computer-agent --yolo-mode --app goal "Get AI trends from ChatGPT, send summary to John on Slack"

# Any macOS app
computer-agent --app chrome "Search for Python tutorials"
```

### Options

```bash
--app APP              # App name (default: Desktop Application)
--yolo-mode            # Auto-approve all actions
--no-rewrite           # Skip automatic goal rewriting
--max-iterations N     # Max steps (default: 40)
--thinking             # Show LLM reasoning
--quiet                # Less output
```

## Architecture

```
src/computer_use_agent/
├── config/
│   ├── prompts.py       # Scrolling + app-specific instructions
│   └── settings.py      # Configuration dataclass
├── actions/
│   ├── executor.py      # Action execution (6x scroll multiplier)
│   └── screen.py        # Screen capture & coordinate handling
├── utils/
│   ├── goal_rewriter.py # Auto goal optimization
│   ├── retry.py         # API retry logic
│   └── llm_logger.py    # Request/response logging
├── agent.py             # Core orchestrator
└── cli.py               # CLI interface
