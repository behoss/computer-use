# General Rules (Reusable)

## CRITICAL: No Unsolicited Documentation

**NEVER create documentation files (README, guides, tutorials, FIXES, SUMMARY, USAGE, etc.) unless EXPLICITLY requested by the user.**

This includes but is not limited to:
- README files
- Usage guides
- Fix summaries
- Tutorial documents
- API documentation
- Architecture documents

Only create standalone documentation files when the user specifically asks for them.

---

## Code Quality Standards

### Architecture Principles
- **Separation of Concerns**: Each module has a single, well-defined responsibility
- **Dependency Injection**: Components receive dependencies rather than creating them
- **Configuration Management**: Use dataclasses for type-safe configuration
- **Error Handling**: Comprehensive error handling with informative messages
- **Type Safety**: Full type hints throughout the codebase

### Code Style
- **Type Hints**: All functions must have parameter and return type hints
- **Docstrings**: All public classes and functions must have one-line docstrings
- **Naming**: Use descriptive names (e.g., `screen_manager` not `sm`)
- **Line Length**: Max 88 characters (Black default)
- **Imports**: Group by stdlib, third-party, local (use isort)
- **Simplicity**: Keep code simple and straightforward - avoid over-engineering
- **Leverage Libraries**: Use well-established libraries instead of custom implementations where they add value
- **Pylance Errors**: All Pylance errors must be addressed before finishing a task

### Testing Approach
- Each module should be independently testable
- Use dependency injection to facilitate mocking
- Configuration should be passed in, not read from environment

### Logging
- Use language-appropriate logging frameworks
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Include context in log messages

## Import Rules

- Use absolute imports within package
- Keep imports organized: stdlib → third-party → local
- Avoid circular dependencies
- Use package initialization files to expose public API

## Documentation Standards

**IMPORTANT: Do NOT add documentation (README, guides, tutorials, etc.) unless explicitly requested by the user.**

When documentation is requested:
- Keep it minimalistic, functional, and no fluff
- Focus on what's needed, not what's nice to have
- Code examples over explanations
- No marketing language or excessive descriptions

Docstrings:
- One-line docstrings for all public functions/classes
- Explain what it does, parameters, return values, exceptions
- Keep concise and technical
- Focus on code over documentation

## Research and Verification

**ALWAYS search online before implementing features or using APIs:**
1. Search for the latest official documentation
2. Verify API methods, parameters, and best practices
3. Check for deprecations or breaking changes
4. Use the most recent stable versions
5. Example workflow:
   - Search for official documentation
   - Verify from authoritative sources
   - Implement using verified patterns and methods
