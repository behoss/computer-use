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

Your task: Rewrite the user's goal to be clearer and more detailed for a vision AI model, but keep it as ONE COMPLETE workflow.

CRITICAL RULES:
- **NEVER SPLIT THE GOAL** - always provide a single, complete workflow
- **DO NOT use the pipe character " | "** - everything should be in one sentence/paragraph
- Make the goal more detailed and explicit about each step
- Use action-oriented language
- Be specific about what to do at each stage

Examples of good rewrites:
Original: "Open ChatGPT, ask about AI, then send to John on Slack"
Rewritten: "Open Chrome and navigate to chatgpt.com, submit a query about recent AI developments, read and capture the response, then switch to Slack, search for John's direct message channel, and send him a message summarizing the AI information from ChatGPT"

Original: "Check my email and respond to the urgent one"
Rewritten: "Open email application, identify the most recent urgent email by scanning subject lines and sender names, read the full email content, then compose and send a response addressing the urgent matter"

Original: "Find the sales report and email it to the team"
Rewritten: "Navigate to the Documents folder, locate the most recent sales report file, open the email application, compose a new message to the sales team distribution list, attach the sales report file, and send the email"

Your task: Rewrite the following goal to be more detailed and explicit, maintaining it as ONE COMPLETE workflow.

Original goal{app_context}: "{original_goal}"

Provide ONLY the rewritten goal as a single complete workflow. NO splitting, NO pipe characters."""

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
