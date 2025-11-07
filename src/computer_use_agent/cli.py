"""Command-line interface for Computer Use Agent."""

import sys
import os
import argparse
import termcolor
import logging
from pathlib import Path
from dotenv import load_dotenv

from .agent import ComputerUseAgent
from .config import AgentConfig, SLACK_INSTRUCTIONS
from .utils import rewrite_goal

logger = logging.getLogger(__name__)


def main():
    """Main entry point for CLI."""
    # Load environment variables from .env file
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Autonomous Agent for macOS Desktop Applications using Gemini Computer Use",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Slack automation with search query language
  %(prog)s --app slack "Search for messages from:@john in:#engineering after:2025-01-01 has:link"
  
  # Generic macOS automation
  %(prog)s --app finder "Create a new folder called 'Projects' on Desktop"
  %(prog)s --app chrome "Search for Python tutorials"
  
  # With thinking enabled for debugging
  %(prog)s --app slack --thinking "Find and summarize today's messages"
  
  # Custom instructions
  %(prog)s --app myapp --instructions "Use F5 to refresh" "Open the dashboard"
        """,
    )

    parser.add_argument("goal", help="What you want to achieve")
    parser.add_argument(
        "--app",
        default="Desktop Application",
        help="Application name (default: Desktop Application)",
    )
    parser.add_argument(
        "--instructions",
        default="",
        help="Custom app-specific instructions",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=40,
        help="Maximum number of steps (default: 40)",
    )
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    parser.add_argument(
        "--thinking",
        action="store_true",
        help="Enable thinking mode for debugging",
    )
    parser.add_argument(
        "--yolo-mode",
        action="store_true",
        help="⚠️  YOLO MODE: Auto-approve ALL actions without confirmation (use at your own risk!)",
    )
    parser.add_argument(
        "--rewrite-goal",
        action="store_true",
        help="Use Gemini 2.5 Flash to automatically rewrite the goal for better results",
    )

    args = parser.parse_args()

    # Check API key
    import os

    if not os.environ.get("GEMINI_API_KEY"):
        termcolor.cprint("❌ Error: GEMINI_API_KEY not set", "red")
        print("Please set your Gemini API key:")
        print("  export GEMINI_API_KEY='your-api-key-here'")
        sys.exit(1)

    # Use built-in Slack instructions if app is Slack
    app_instructions = args.instructions
    if args.app.lower() == "slack" and not args.instructions:
        app_instructions = SLACK_INSTRUCTIONS

    # Rewrite goal if requested
    final_goal = args.goal
    original_goal = ""
    if args.rewrite_goal:
        print("\n🔄 Rewriting goal with Gemini 2.5 Flash...")
        print(f"📝 Original: {args.goal}")
        rewritten = rewrite_goal(args.goal, args.app)

        # Handle multi-part goals (split by |)
        if " | " in rewritten:
            goals = [g.strip() for g in rewritten.split(" | ")]
            print(f"\n✨ Rewritten into {len(goals)} parts:")
            for i, goal in enumerate(goals, 1):
                print(f"   Part {i}: {goal}")
            final_goal = goals[0]  # Use first part
            original_goal = args.goal  # Save original
            print(f"\n▶️  Executing Part 1: {final_goal}")
            if len(goals) > 1:
                print(f"   (Part 2 will need to be run separately)")
        else:
            print(f"✨ Rewritten: {rewritten}\n")
            final_goal = rewritten
            original_goal = args.goal  # Save original

    # Show YOLO mode warning if enabled
    if args.yolo_mode:
        termcolor.cprint("\n⚠️  YOLO MODE ENABLED ⚠️", "yellow", attrs=["bold"])
        termcolor.cprint("All safety confirmations will be AUTO-APPROVED!", "yellow")
        termcolor.cprint("You take full responsibility for all actions.\n", "yellow")

    # Create configuration
    config = AgentConfig(
        goal=final_goal,
        original_goal=original_goal,
        app_name=args.app,
        app_instructions=app_instructions,
        max_iterations=args.max_iterations,
        verbose=not args.quiet,
        enable_thinking=args.thinking,
        yolo_mode=args.yolo_mode,
    )

    try:
        # Initialize and run agent
        agent = ComputerUseAgent(config)
        success = agent.run()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Agent interrupted")
        sys.exit(130)
    except Exception as e:
        termcolor.cprint(f"❌ Fatal error: {e}", "red")
        logger.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    main()
