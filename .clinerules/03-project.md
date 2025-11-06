# Project-Specific Rules (Computer Use Agent)

## Project Structure

This is a production-ready Python package using best practices architecture:

```
computer-use/
├── src/computer_use_agent/     # Main package
│   ├── actions/                # Action execution layer
│   ├── config/                 # Configuration & prompts
│   ├── utils/                  # Utilities (retry, response handling)
│   ├── agent.py                # Core orchestrator
│   └── cli.py                  # CLI interface
├── autonomous_agent.py         # Legacy PoC (maintained for compatibility)
├── pyproject.toml              # Project metadata & dependencies
└── README.md                   # Documentation
```

## File Organization Rules

### Config Layer (`src/computer_use_agent/config/`)
- `settings.py`: Configuration dataclasses
- `prompts.py`: System prompts and instructions
- No business logic, only configuration

### Actions Layer (`src/computer_use_agent/actions/`)
- `executor.py`: Action execution logic
- `screen.py`: Screen/coordinate management
- Each action handler is a private method
- No direct API calls, only desktop automation

### Utils Layer (`src/computer_use_agent/utils/`)
- `response_handler.py`: Response processing utilities
- `retry.py`: Retry logic with exponential backoff
- Pure functions where possible
- No application state

### Core Layer
- `agent.py`: Main orchestrator, coordinates all components
- `cli.py`: Command-line interface only
- Minimal business logic in CLI

## Version Control

- Keep `autonomous_agent.py` for backward compatibility
- Mark deprecated code with warnings
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Update CHANGELOG for significant changes
