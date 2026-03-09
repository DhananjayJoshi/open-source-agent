"""
Step 1: GitHub API fetcher
Fetches open issues from a repo with pluggable filters.
"""

from typing import Any

import requests

EASY_LABELS = [
    "good first issue",
    "easy",
    "beginner",
    "beginner-friendly",
    "help wanted",
    "starter",
]


def fetch_issues(
    repo: str,
    token: str,
    state: str = "open",
    per_page: int = 50,
    labels: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Fetch issues from a GitHub repo via the API."""
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    params = {"state": state, "per_page": per_page}
    if labels:
        params["labels"] = ",".join(labels)

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    # Exclude pull requests (GitHub returns PRs in /issues too)
    return [i for i in response.json() if "pull_request" not in i]


def fetch_easy_labeled_issues(repo: str, token: str) -> list[dict[str, Any]]:
    """Fetch issues that already have easy/beginner labels."""
    all_issues = []
    for label in EASY_LABELS:
        try:
            issues = fetch_issues(repo, token, labels=[label])
            all_issues.extend(issues)
        except requests.HTTPError:
            continue

    # Deduplicate by issue number
    seen = set()
    unique = []
    for issue in all_issues:
        if issue["number"] not in seen:
            seen.add(issue["number"])
            unique.append(issue)
    return unique


def fetch_all_open_issues(
    repo: str, token: str, limit: int = 100
) -> list[dict[str, Any]]:
    """Fetch all open issues (no label filter) up to limit."""
    issues = []
    page = 1
    while len(issues) < limit:
        url = f"https://api.github.com/repos/{repo}/issues"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "state": "open",
            "per_page": min(50, limit - len(issues)),
            "page": page,
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        batch = [i for i in response.json() if "pull_request" not in i]
        if not batch:
            break
        issues.extend(batch)
        page += 1
    return issues
