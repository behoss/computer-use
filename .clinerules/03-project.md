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
- `goal_rewriter.py`: Goal rewriting with inline context injection
- Pure functions where possible
- No application state

### Core Layer
- `agent.py`: Main orchestrator, coordinates all components
- `cli.py`: Command-line interface only
- Minimal business logic in CLI

## Architecture Decisions

### Goal Rewriting with Inline Context Injection

**Design Pattern**: Context is injected inline during goal rewriting, not in the main system prompt.

**Rationale**:
- **Lean system prompt**: Keep main prompt generic and universally useful
- **Task-specific context**: Each goal gets exactly the contextual help it needs
- **Scalability**: Add new apps by updating goal rewriter only, not system prompt
- **Token efficiency**: Avoid bloating every API call with app-specific details

**Implementation**:
- `goal_rewriter.py` uses Gemini 2.5 Pro to rewrite goals
- Detects apps involved (Slack, Linear, VSCode, Cline, etc.)
- Injects relevant shortcuts, tips, and workflow patterns INLINE at each step
- Example: "press command+k to open command palette, type 'ENG-123' to search for the issue (Linear issues use format like ENG-123), then press Return to open it"

**What Goes in System Prompt**:
- Generic macOS keyboard shortcuts (command+c/v, command+tab)
- Keyboard-first interaction principles
- Input field submission patterns
- Cookie/privacy dialog handling
- Safety decision guidelines

**What Goes in Goal Rewriter**:
- App-specific keyboard shortcuts (Linear's command+shift+., Slack's command+k)
- App-specific tips (Cline wait times, Slack search syntax)
- Workflow patterns (Linear → VSCode git branch creation)
- Context for specific actions being performed

**Benefits**:
- Faster, cheaper API calls (less tokens in system prompt)
- Goals are enriched with exactly what's needed for that task
- Easy to add new apps without modifying core system prompt
- Context adapts to actual task, not generic coverage

## Version Control

- Keep `autonomous_agent.py` for backward compatibility
- Mark deprecated code with warnings
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Update CHANGELOG for significant changes
