"""Goal rewriting utility using Gemini 2.5 Flash."""

import os
from google import genai
from google.genai import types


class GoalRewriter:
    """Rewrites user goals to be more effective and safer for Computer Use."""

    def __init__(self):
        """Initialize the goal rewriter."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        self.client = genai.Client(api_key=api_key)

    def rewrite_goal(self, original_goal: str, app_name: str = "") -> str:
        """Rewrite a goal to be more effective for Computer Use.

        Args:
            original_goal: The user's original goal
            app_name: The target application name (optional)

        Returns:
            Rewritten goal that is clearer and safer
        """
        app_context = f" in {app_name}" if app_name else ""

        prompt = f"""You are an expert at rewriting user intentions for a Computer Use automation system.

Your task is to rewrite the user's goal to make it:
1. Clear and actionable for a computer automation agent
2. Safe by splitting consequential actions from informational ones
3. Specific about what to observe vs what to execute
4. Structured to avoid safety filtering

RULES:
- If the goal involves a consequential action (sending messages, making purchases, installing software, deleting data), split it into TWO parts:
  Part 1: Navigate and gather information (report what you see)
  Part 2: Execute the action (only if explicitly needed)
  
- For informational tasks, make them clear and specific
- Use action verbs: "Navigate to", "Check", "Report", "Observe", "Find"
- Avoid vague language like "deal with" or "handle"
- Be explicit about what information to gather vs what actions to take

Original goal{app_context}: "{original_goal}"

Rewrite this goal to be more effective. If it's a consequential action, split it into information gathering first.
Only provide the rewritten goal(s), nothing else. If splitting into multiple goals, separate them with " | " (pipe character)."""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                ),
            )

            if response and response.candidates and response.text:
                rewritten = response.text.strip()
                return rewritten
            else:
                # Fallback to original if rewriting fails
                return original_goal

        except Exception as e:
            print(f"⚠️  Goal rewriting failed: {e}")
            print(f"   Using original goal instead.")
            return original_goal


def rewrite_goal(goal: str, app_name: str = "") -> str:
    """Convenience function to rewrite a goal.

    Args:
        goal: Original user goal
        app_name: Target application name (optional)

    Returns:
        Rewritten goal
    """
    rewriter = GoalRewriter()
    return rewriter.rewrite_goal(goal, app_name)
