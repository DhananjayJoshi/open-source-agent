"""
OSS Contributor Agent - LangGraph Structure
"""

from langgraph.graph import END, StateGraph

from nodes import (
    analyze_issues,
    discover_repos,
)
from state import AgentState


def should_continue_after_validation(state: AgentState) -> str:
    """Route after fix validation."""
    if state["validation_passed"]:
        return "create_pr"
    elif state["retry_count"] < 3:
        return "fix_issue"  # retry
    else:
        return "handle_error"


def should_continue_after_issues(state: AgentState) -> str:
    """Route after issue analysis."""
    if state["selected_issues"]:
        return "select_issue"
    else:
        return "handle_error"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # ── Nodes ──────────────────────────────────────────────────────────────
    graph.add_node("discover_repos", discover_repos)
    graph.add_node("analyze_issues", analyze_issues)
    # graph.add_node("select_issue", select_issue)
    # graph.add_node("fix_issue", fix_issue)
    # graph.add_node("validate_fix", validate_fix)
    # graph.add_node("create_pr", create_pr)
    # graph.add_node("handle_error", handle_error)

    # ── Edges ──────────────────────────────────────────────────────────────
    graph.set_entry_point("discover_repos")
    graph.add_edge("discover_repos", "analyze_issues")

    # graph.add_conditional_edges(
    #     "analyze_issues",
    #     should_continue_after_issues,
    #     {
    #         "select_issue": "select_issue",
    #         "handle_error": "handle_error",
    #     },
    # )

    # graph.add_edge("select_issue", "fix_issue")

    # graph.add_conditional_edges(
    #     "validate_fix",
    #     should_continue_after_validation,
    #     {
    #         "create_pr": "create_pr",
    #         "fix_issue": "fix_issue",  # retry with feedback
    #         "handle_error": "handle_error",
    #     },
    # )

    # graph.add_edge("fix_issue", "validate_fix")
    # graph.add_edge("create_pr", END)
    graph.add_edge("analyze_issues", END)

    return graph.compile()
