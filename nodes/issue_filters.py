"""
Step 2: Heuristic filters
Lightweight, no-LLM filters to pre-rank issues before expensive LLM calls.
Each filter takes a list of issues and returns a filtered/scored list.
Filters are composable — chain them via `apply_filters()`.
"""

from typing import Any, Callable

Issue = dict[str, Any]
Filter = Callable[[list[Issue]], list[Issue]]

EASY_LABELS = {
    "good first issue",
    "easy",
    "beginner",
    "beginner-friendly",
    "help wanted",
    "starter",
}
SKIP_LABELS = {
    "wontfix",
    "duplicate",
    "invalid",
    "blocked",
    "needs design",
    "needs discussion",
    "epic",
}


# ── Individual filters ──────────────────────────────────────────────────────


def filter_no_assignee(issues: list[Issue]) -> list[Issue]:
    """Keep only unassigned issues (no one is already working on it)."""
    return [i for i in issues if not i.get("assignee")]


def filter_low_comments(issues: list[Issue], max_comments: int = 5) -> list[Issue]:
    """Keep issues with few comments — highly debated issues are rarely easy."""
    return [i for i in issues if i.get("comments", 0) <= max_comments]


def filter_no_linked_pr(issues: list[Issue]) -> list[Issue]:
    """Keep issues without a linked PR (not already being worked on)."""
    return [i for i in issues if not i.get("pull_request")]


def filter_skip_labels(issues: list[Issue]) -> list[Issue]:
    """Remove issues tagged with labels that signal complexity or blockers."""

    def has_skip_label(issue: Issue) -> bool:
        labels = {l["name"].lower() for l in issue.get("labels", [])}
        return bool(labels & SKIP_LABELS)

    return [i for i in issues if not has_skip_label(issue=i)]


def filter_short_title(issues: list[Issue], max_words: int = 15) -> list[Issue]:
    """Keep issues with short, focused titles (long titles often = complex issues)."""
    return [i for i in issues if len(i.get("title", "").split()) <= max_words]


def filter_has_body(issues: list[Issue], min_chars: int = 20) -> list[Issue]:
    """Keep issues with enough description to understand what needs to be done."""
    return [i for i in issues if len(i.get("body") or "") >= min_chars]


def filter_not_too_long(issues: list[Issue], max_chars: int = 3000) -> list[Issue]:
    """Skip issues with very long bodies — usually complex bugs or feature requests."""
    return [i for i in issues if len(i.get("body") or "") <= max_chars]


def boost_easy_labels(issues: list[Issue]) -> list[Issue]:
    """Sort issues so those with easy/beginner labels appear first."""

    def has_easy_label(issue: Issue) -> bool:
        labels = {l["name"].lower() for l in issue.get("labels", [])}
        return bool(labels & EASY_LABELS)

    return sorted(issues, key=lambda i: (not has_easy_label(i), i.get("comments", 0)))


# ── Composable pipeline ─────────────────────────────────────────────────────

DEFAULT_FILTERS: list[Filter] = [
    filter_no_assignee,
    filter_no_linked_pr,
    filter_skip_labels,
    filter_has_body,
    filter_not_too_long,
    lambda issues: filter_low_comments(issues, max_comments=5),
    boost_easy_labels,
]


def apply_filters(
    issues: list[Issue], filters: list[Filter] = DEFAULT_FILTERS
) -> list[Issue]:
    """
    Apply a list of filter functions sequentially.
    Pluggable: pass your own list to customize behavior.

    Example:
        my_filters = [filter_no_assignee, filter_low_comments]
        results = apply_filters(issues, filters=my_filters)
    """
    for f in filters:
        issues = f(issues)
    return issues
