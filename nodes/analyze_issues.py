"""
NODE 2 — Analyze issues
"""

import os
from dataclasses import dataclass

import llm
from github_fetcher import fetch_all_open_issues, fetch_easy_labeled_issues
from state import AgentState

from .issue_filters import DEFAULT_FILTERS, Filter, apply_filters
from .issue_scorer import IssueScore, score_issues


@dataclass
class RepoResult:
    repo: str
    total_fetched: int
    after_filters: int
    scores: list[IssueScore]

    def easy_issues(self) -> list[IssueScore]:
        return [s for s in self.scores if s.difficulty == "easy"]

    def print_summary(self):
        print(f"\n{'=' * 60}")
        print(f"📦 {self.repo}")
        print(
            f"   Fetched: {self.total_fetched} → After filters: {self.after_filters} → Scored: {len(self.scores)}"
        )
        print(f"   ✅ Easy issues: {len(self.easy_issues())}")
        for s in self.scores:
            tag = (
                "🟢"
                if s.difficulty == "easy"
                else "🟡"
                if s.difficulty == "medium"
                else "🔴"
            )
            beginner = "👶 beginner-friendly" if s.good_for_beginner else ""
            print(f"\n   {tag} #{s.issue_number} — {s.title}")
            print(
                f"      Difficulty: {s.difficulty} | ~{s.estimated_hours}h {beginner}"
            )
            print(f"      Why: {s.reason}")
            print(f"      Approach: {s.suggested_approach}")


def analyze_issues(state: AgentState) -> dict:
    """Collect open issues from discovered repos and rank them by AI-fixability."""
    print("\n📋 [analyze_issues] Collecting issues...")

    repos = state["discovered_repos"]
    repoNames = [r["full_name"] for r in repos]
    ghToken = os.getenv("GITHUB_TOKEN")

    results = run_pipeline(
        repos=repoNames,
        github_token=str(ghToken),
        llm=llm.get_llm(),
        top_n=15,
    )

    for result in results:
        result.print_summary()

    # Easy issues across all repos
    print("\n\n🎯 All easy issues across repos:")
    for result in results:
        for issue in result.easy_issues():
            print(f"  {result.repo}#{issue.issue_number} — {issue.title}")

    return {}


def run_pipeline(
    repos: list[str],
    github_token: str,
    llm,  # pluggable: any LangChain ChatModel
    top_n: int = 20,  # max issues to pass to LLM per repo
    filters: list[Filter] = DEFAULT_FILTERS,  # pluggable: swap or extend filters
    use_label_fetch: bool = True,  # try label-based fetch first
) -> list[RepoResult]:
    """
    Run the full hybrid pipeline on a list of repos.

    Args:
        repos:            List of "owner/repo" strings
        github_token:     GitHub personal access token
        llm:              LangChain ChatModel (OpenAI, Ollama, OpenRouter, etc.)
        top_n:            Max issues per repo to send to LLM
        filters:          List of filter functions (swap out as needed)
        use_label_fetch:  If True, try fetching easy-labeled issues first

    Returns:
        List of RepoResult objects with scores
    """
    results = []

    for repo in repos:
        print(f"\n🔍 Processing {repo}...")

        # Step 1: Fetch
        if use_label_fetch:
            issues = fetch_easy_labeled_issues(repo, github_token)
            # Fall back to all issues if labeled fetch returns too few
            if len(issues) < 5:
                print(
                    f"   ⚠️  Only {len(issues)} labeled issues, fetching all open issues..."
                )
                issues = fetch_all_open_issues(repo, github_token, limit=100)
        else:
            issues = fetch_all_open_issues(repo, github_token, limit=100)

        total_fetched = len(issues)
        print(f"   Fetched {total_fetched} issues")

        # Step 2: Heuristic filter
        filtered = apply_filters(issues, filters=filters)
        filtered = filtered[:top_n]  # cap before sending to LLM
        print(f"   After filters: {len(filtered)} issues")

        if not filtered:
            print("   ⚠️  No issues passed filters, skipping LLM scoring")
            results.append(RepoResult(repo, total_fetched, 0, []))
            continue

        # Step 3: LLM score
        scores = score_issues(filtered, llm=llm)

        results.append(
            RepoResult(
                repo=repo,
                total_fetched=total_fetched,
                after_filters=len(filtered),
                scores=scores,
            )
        )

    return results
