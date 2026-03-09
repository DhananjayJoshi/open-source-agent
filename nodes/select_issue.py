"""
NODE 3 — Select issue
"""

from langchain_core.messages import HumanMessage

from state import AgentState


def select_issue(state: AgentState) -> dict:
    """Pick the top-ranked issue and load the repo context for fixing."""
    issue = state["selected_issues"][0]
    print(f"\n🎯 [select_issue] Working on: {issue['title']}")

    return {
        "current_issue": issue,
        "retry_count": 0,
        "messages": [HumanMessage(content=f"Selected issue: {issue['url']}")],
    }
