"""
Step 3: LLM Scorer
Uses structured output to score each issue for fixability.
Pluggable: swap any LangChain-compatible ChatModel (OpenAI, Ollama, OpenRouter).
"""

from typing import Any, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

# ── Output schema ───────────────────────────────────────────────────────────


class IssueScore(BaseModel):
    issue_number: int
    title: str
    difficulty: Literal["easy", "medium", "hard"]
    estimated_hours: int = Field(description="Rough estimate to fix, in hours")
    reason: str = Field(description="One sentence explaining the difficulty rating")
    good_for_beginner: bool
    suggested_approach: str = Field(
        description="Brief hint on how to tackle this issue"
    )


class IssueScoreList(BaseModel):
    issues: list[IssueScore]


# ── Prompt ──────────────────────────────────────────────────────────────────

SCORER_SYSTEM_PROMPT = """
You are an expert open source contributor helping developers find beginner-friendly issues.

For each GitHub issue provided, evaluate:
- How hard it is to fix (easy/medium/hard)
- Estimated hours to complete
- Whether it's suitable for a beginner contributor
- A brief suggested approach

Be pragmatic. An "easy" issue should be fixable in under 4 hours by someone
familiar with the language but new to the codebase.
""".strip()


def format_issues_for_prompt(
    issues: list[dict[str, Any]], max_body_chars: int = 500
) -> str:
    """Format a list of raw GitHub issues into a prompt-friendly string."""
    lines = []
    for issue in issues:
        body = (issue.get("body") or "")[:max_body_chars]
        labels = ", ".join(l["name"] for l in issue.get("labels", []))
        lines.append(
            f"Issue #{issue['number']}: {issue['title']}\n"
            f"Labels: {labels or 'none'}\n"
            f"Comments: {issue.get('comments', 0)}\n"
            f"Body: {body}\n"
            f"---"
        )
    return "\n".join(lines)


# ── Scorer ──────────────────────────────────────────────────────────────────


def score_issues(
    issues: list[dict[str, Any]],
    llm,  # Any LangChain ChatModel
    batch_size: int = 10,
) -> list[IssueScore]:
    """
    Score a list of GitHub issues using an LLM with structured output.

    Args:
        issues:     Pre-filtered list of GitHub issue dicts
        llm:        Any LangChain-compatible ChatModel (pluggable)
        batch_size: How many issues to score per LLM call

    Returns:
        Flat list of IssueScore objects, sorted by easiest first

    Example:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o-mini")
        scores = score_issues(issues, llm)
    """
    structured_llm = llm.with_structured_output(IssueScoreList)
    all_scores: list[IssueScore] = []

    for i in range(0, len(issues), batch_size):
        batch = issues[i : i + batch_size]
        prompt = format_issues_for_prompt(batch)

        result: IssueScoreList = structured_llm.invoke(
            [
                SystemMessage(content=SCORER_SYSTEM_PROMPT),
                HumanMessage(content=f"Score these GitHub issues:\n\n{prompt}"),
            ]
        )
        all_scores.extend(result.issues)

    # Sort: easy first, then by estimated hours
    return sorted(
        all_scores,
        key=lambda s: (
            {"easy": 0, "medium": 1, "hard": 2}[s.difficulty],
            s.estimated_hours,
        ),
    )
