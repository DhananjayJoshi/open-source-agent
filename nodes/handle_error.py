"""
NODE 7 — Handle error
"""

from langchain_core.messages import AIMessage

from state import AgentState


def handle_error(state: AgentState) -> dict:
    """Handle errors and print diagnostic information."""
    error_msg = (
        state.get("error") or state.get("validation_feedback") or "Unknown error"
    )
    print(f"\n❌ [handle_error] {error_msg}")
    return {
        "messages": [AIMessage(content=f"Agent stopped: {error_msg}")],
    }
