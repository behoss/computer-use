# Development Workflow

## Debugging and Testing

**When stuck or testing functionality in isolation:**
- Create test scripts in `scripts/` folder
- Use these to assess how things work by inspecting logs
- Test individual components before integrating
- Keep scripts for future reference

## Major Changes and Refactoring

**IMPORTANT: Before any rearchitecting or major structural changes:**
1. Consult with the user first
2. Present multiple options with pros/cons
3. Get explicit approval before proceeding
4. Major changes include: moving files, changing architecture, large refactors

## Adding New Features

1. Identify which layer the feature belongs to (actions/config/utils/core)
2. Create or modify the appropriate module
3. Update type hints and docstrings
4. Update CLI if needed

## Modifying Existing Code

1. Check which module owns the functionality
2. Make changes following single responsibility principle
3. Update dependent modules if interfaces change
4. Verify type hints still match

## Package Updates

1. Always check PyPI for latest stable versions
2. Use `uv add package` for automatic latest version
3. Test after updates to ensure compatibility
4. Update version in pyproject.toml if making a release
