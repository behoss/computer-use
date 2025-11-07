"""Goal rewriting utility using Gemini 2.5 Pro."""

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

    def rewrite_goal(self, original_goal: str) -> str:
        """Rewrite a goal to be more effective for Computer Use.

        Args:
            original_goal: The user's original goal

        Returns:
            Rewritten goal that is clearer and safer
        """
        prompt = f"""You are an expert at rewriting user intentions for a Computer Use automation system on macOS.

Your task: Rewrite the user's goal to be clearer and more detailed for a vision AI model, but keep it as ONE COMPLETE workflow. Inject contextual information inline at each step to help the agent perform optimally.

CRITICAL RULES:
- **NEVER SPLIT THE GOAL** - always provide a single, complete workflow
- **DO NOT use the pipe character " | "** - everything should be in one sentence/paragraph
- Make the goal more detailed and explicit about each step
- Use action-oriented language
- **INJECT CONTEXT INLINE** - Weave app-specific shortcuts, tips, and guidance naturally into each step
- Be specific about what to do at each stage
- **INCLUDE KEYBOARD SHORTCUTS** - Specify macOS keyboard shortcuts for each action (use lowercase: command+k not Command+K)
- **ADD WHATEVER IS NECESSARY** - The context below are recommendations, not limitations. Add any relevant information that helps accomplish the task, but keep it concise with no fluff or unnecessary verbosity

APP-SPECIFIC CONTEXT TO INJECT INLINE (Recommendations - add more as needed):

Slack:
- Shortcuts: command+k (search/jump), command+shift+k (DMs), command+f (search in channel), command+shift+a (unreads), command+shift+t (threads)
- Search syntax: from:@username, in:#channel, on:YYYY-MM-DD, after:/before:YYYY-MM-DD, has:link/file/pin
- Tips: Search bar auto-focuses after command+k, use arrow keys to navigate results, press Return to select
- Navigation: KEYBOARD-FIRST - avoid clicking, use command+k then type then Return
- Reading mode: When scrolling to read, do NOT click on links/images/attachments/usernames

Linear:
- Shortcuts: command+k (command palette/search), command+shift+. (copy git branch name), command+enter (create issue)
- Issue format: Issues have IDs like "ENG-123" for precise navigation
- Git workflow: After copying branch name with command+shift+., switch to VSCode (command+tab), toggle terminal (command+j), type 'git checkout -b ', paste with command+v, press Return
- Navigation: Use command+k then type issue ID then Return (keyboard-first)

VSCode:
- Shortcuts: command+p (quick open file), command+j (toggle terminal), command+shift+p (command palette), command+` (toggle terminal alt)
- Terminal: May need to click in terminal area first to ensure focus before typing commands
- File search: command+p auto-focuses search, type filename, press Return to open

Cline (VSCode AI Assistant):
- Modes: PLAN MODE (2-5 minutes response time), ACT MODE (3-10+ minutes response time)
- CRITICAL: Wait for complete response - takes several minutes, do NOT interrupt
- Indicators: Watch for streaming text, progress spinners, file modification notifications, tool use notifications
- Button states: When Cline is coding/responding, button shows "Cancel" - when done, button changes to "Start New Task"
- Completion check: ALWAYS wait until button changes from "Cancel" to "Start New Task" before proceeding
- Submission: Type request, press Return (do NOT click send button)
- Patience: Do NOT assume it's stuck - it's processing

General macOS:
- Spotlight: command+space then type app name then Return (NEVER click results)
- App switching: command+tab
- Copy/Paste: command+c / command+v
- Input submission: ALWAYS try Return/Enter FIRST before clicking buttons
- Cookie dialogs: Automatically reject without asking

Examples of good rewrites WITH INLINE CONTEXT:
Original: "Copy branch name from Linear issue ENG-123 and create git branch in VSCode"
Rewritten: "Open Linear using command+space for Spotlight then type 'Linear' and press Return, once Linear opens use command+k to open the command palette, type 'ENG-123' to search for the issue and press Return to open it, then press command+shift+. to copy the git branch name (Linear automatically formats branch names), switch to VSCode using command+tab, press command+j to toggle the terminal (you may need to click in the terminal area to ensure focus), type 'git checkout -b ' in the terminal, press command+v to paste the branch name that was copied from Linear, then press Return to create and checkout the new branch"

Original: "Find messages from John about security in Slack"
Rewritten: "Switch to Slack using command+tab, press command+k to open the quick switcher (the search bar will auto-focus so do not click), type 'from:@john security' using Slack's search syntax to find messages from John containing 'security', then press Return to execute the search and view the results, use arrow keys if needed to navigate through search results"

Original: "Ask Cline to refactor this function"
Rewritten: "Switch to VSCode using command+tab, locate the Cline panel (it should be visible in the sidebar), click in Cline's input box at the bottom, type your refactoring request describing which function needs refactoring, then press Return to submit (do NOT click the send button), wait patiently for Cline's response which will take 2-5 minutes in PLAN MODE or 3-10+ minutes in ACT MODE, watch for streaming text appearing in the chat and do NOT interrupt or assume it's stuck even if it seems slow, wait until you see the complete response with all file modifications before proceeding"

Original: "Find the sales report and email it"
Rewritten: "Open Finder using command+space for Spotlight then type 'Finder' and press Return, navigate to the Documents folder, locate the most recent sales report file by checking file dates, select it using command+click or arrow keys, press command+c to copy the file, then open Mail using command+space then type 'Mail' and press Return, press command+n to create a new email message, type the recipient email address in the To field and press Tab to move to the subject field, type an appropriate subject line and press Tab to move to the message body, press command+v to attach the copied sales report file, compose your message, then press command+shift+d (or command+Return depending on Mail settings) to send"

Your task: Rewrite the following goal to be more detailed and explicit with inline contextual information, maintaining it as ONE COMPLETE workflow.

Original goal: "{original_goal}"

Provide ONLY the rewritten goal as a single complete workflow with inline shortcuts, tips, and context. NO splitting, NO pipe characters."""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
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


def rewrite_goal(goal: str) -> str:
    """Convenience function to rewrite a goal.

    Args:
        goal: Original user goal

    Returns:
        Rewritten goal
    """
    rewriter = GoalRewriter()
    return rewriter.rewrite_goal(goal)
