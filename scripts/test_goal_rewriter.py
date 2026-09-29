#!/usr/bin/env python3
"""Test script for goal rewriter with various test cases."""

import sys
import os
from pathlib import Path

# Add parent directory to path to import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.computer_use_agent.utils.goal_rewriter import rewrite_goal

# Load environment variables
load_dotenv()

# Test cases covering different scenarios
TEST_CASES = [
    # Slack-related
    {
        "goal": "Find messages from John about the security bug in Slack",
        "description": "Slack search with user mention",
    },
    {
        "goal": "Read all messages in #engineering channel from today in Slack",
        "description": "Slack channel reading",
    },
    # Linear-related
    {
        "goal": "Copy branch name from Linear issue ENG-123",
        "description": "Linear branch copy",
    },
    {
        "goal": "Copy branch name from Linear issue ENG-456 and create git branch in VSCode",
        "description": "Linear to VSCode git workflow",
    },
    # Cline-related
    {
        "goal": "Ask Cline to refactor the authentication function in VSCode",
        "description": "Cline refactoring request",
    },
    # Multi-app workflows
    {
        "goal": "Search ChatGPT for Python best practices, then send summary to #team channel in Slack",
        "description": "Multi-app: ChatGPT to Slack",
    },
    # Generic macOS
    {
        "goal": "Create a new folder called Projects on Desktop",
        "description": "Simple Finder operation",
    },
    # Complex workflow
    {
        "goal": "Find the latest sales report in Downloads, email it to team@company.com",
        "description": "File search and email workflow",
    },
]


def test_rewriter():
    """Test the goal rewriter with various cases."""
    print("=" * 80)
    print("GOAL REWRITER TEST SUITE")
    print("=" * 80)
    print()

    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY not set")
        print("Please set your Gemini API key in .env file")
        sys.exit(1)

    results = []

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'─' * 80}")
        print(f"TEST CASE {i}/{len(TEST_CASES)}: {test_case['description']}")
        print(f"{'─' * 80}")
        print(f"📝 Original Goal: {test_case['goal']}")
        print()

        try:
            rewritten = rewrite_goal(test_case["goal"])
            print(f"✨ Rewritten Goal:")
            print(f"   {rewritten}")
            print()

            # Check quality indicators
            has_shortcuts = any(
                kw in rewritten.lower() for kw in ["command+", "press ", "return"]
            )
            has_inline_context = "(" in rewritten  # Parenthetical context
            word_count = len(rewritten.split())

            quality = {
                "has_shortcuts": has_shortcuts,
                "has_inline_context": has_inline_context,
                "word_count": word_count,
                "concise": 30 < word_count < 200,  # Reasonable length
            }

            print(f"📊 Quality Check:")
            print(f"   ✓ Keyboard shortcuts included: {quality['has_shortcuts']}")
            print(
                f"   ✓ Inline context (parentheticals): {quality['has_inline_context']}"
            )
            print(
                f"   ✓ Word count: {quality['word_count']} {'✓' if quality['concise'] else '⚠️  (too verbose or too short)'}"
            )

            results.append(
                {
                    "test_case": test_case,
                    "rewritten": rewritten,
                    "quality": quality,
                }
            )

        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(
                {
                    "test_case": test_case,
                    "error": str(e),
                }
            )

    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")

    successful = sum(1 for r in results if "rewritten" in r)
    failed = len(results) - successful

    print(f"✅ Successful: {successful}/{len(TEST_CASES)}")
    print(f"❌ Failed: {failed}/{len(TEST_CASES)}")

    if successful > 0:
        avg_words = (
            sum(r["quality"]["word_count"] for r in results if "quality" in r)
            / successful
        )
        shortcuts_count = sum(
            1 for r in results if r.get("quality", {}).get("has_shortcuts", False)
        )
        context_count = sum(
            1 for r in results if r.get("quality", {}).get("has_inline_context", False)
        )

        print(f"\n📊 Quality Metrics:")
        print(f"   Average word count: {avg_words:.1f}")
        print(f"   Tests with keyboard shortcuts: {shortcuts_count}/{successful}")
        print(f"   Tests with inline context: {context_count}/{successful}")

    print()


if __name__ == "__main__":
    test_rewriter()
