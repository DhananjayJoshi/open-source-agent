"""
NODE 6 — Create PR
"""

from langchain_core.messages import AIMessage

from state import AgentState


def create_pr(state: AgentState) -> dict:
    """Commit changes to a new branch and open a pull request."""
    issue = state["current_issue"]
    changes = state["code_changes"]
    repo_name = issue["repo"]["full_name"]

    print(f"\n🚀 [create_pr] Creating PR on {repo_name}...")

    # Note: gh (GitHub client) would be initialized here if available
    # This is a placeholder for GitHub API integration

    # In a full implementation:
    # repo = gh.get_repo(repo_name)
    # branch_name = f"ai-fix/issue-{issue['number']}"
    # base_sha = repo.get_branch(repo.default_branch).commit.sha
    # ... create branch and commit changes ...
    # pr = repo.create_pull(...)

    pr_url = f"https://github.com/{repo_name}/pull/0"  # placeholder
    print(f"   🎉 PR created: {pr_url}")

    return {
        "pr_url": pr_url,
        "messages": [AIMessage(content=f"PR created: {pr_url}")],
    }
