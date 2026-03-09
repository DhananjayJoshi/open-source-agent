"""
Shared state flowing through every node in the graph.
"""

from typing import Annotated, Optional, TypedDict

from langgraph.graph.message import add_messages
from pydantic import BaseModel


class RepoInfo(TypedDict):
    full_name: str  # e.g.  "django/django"
    url: str
    stars: int
    language: str
    topics: list[str]


class RepoList(BaseModel):
    repos: list[RepoInfo]


class IssueInfo(TypedDict):
    number: int
    title: str
    body: str
    labels: list[str]
    url: str
    repo: RepoInfo


class CodeChange(TypedDict):
    file_path: str
    original_content: str
    new_content: str
    explanation: str


class AgentState(TypedDict):
    # ── Config (provided by caller) ──────────────────────────────────────
    topic: str  # e.g. "python", "web"
    language: str  # e.g. "Python", "TypeScript"
    max_repos: int
    max_issues_per_repo: int

    # ── Discovery ────────────────────────────────────────────────────────
    discovered_repos: list[RepoInfo]

    # ── Issue analysis ───────────────────────────────────────────────────
    selected_issues: list[IssueInfo]  # ranked candidates
    current_issue: Optional[IssueInfo]

    # ── Fix ──────────────────────────────────────────────────────────────
    code_changes: list[CodeChange]
    fix_explanation: str

    # ── Validation ───────────────────────────────────────────────────────
    validation_passed: bool
    validation_feedback: str  # fed back into fix_issue on retry
    retry_count: int

    # ── PR ───────────────────────────────────────────────────────────────
    pr_url: Optional[str]

    # ── Conversation log (LangGraph message reducer) ─────────────────────
    messages: Annotated[list, add_messages]

    # ── Error handling ───────────────────────────────────────────────────
    error: Optional[str]
