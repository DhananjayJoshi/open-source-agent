"""
Entry point — run the OSS Contributor Agent.

Usage:
    python main.py
    python main.py --topic fastapi --language Python --max-repos 3
"""

import argparse

from dotenv import load_dotenv

# load environment variables before importing project modules that depend on them
load_dotenv()

from graph import build_graph


def main():
    parser = argparse.ArgumentParser(description="OSS Contributor Agent")
    parser.add_argument("--topic", default="python", help="GitHub topic to search")
    parser.add_argument("--language", default="Python", help="Programming language")
    parser.add_argument("--max-repos", type=int, default=5, help="Repos to scan")
    parser.add_argument("--max-issues", type=int, default=3, help="Issues per repo")
    args = parser.parse_args()

    graph = build_graph()

    initial_state = {
        "topic": args.topic,
        "language": args.language,
        "max_repos": args.max_repos,
        "max_issues_per_repo": args.max_issues,
        # Initialise all other fields
        "discovered_repos": [],
        "selected_issues": [],
        "current_issue": None,
        "code_changes": [],
        "fix_explanation": "",
        "validation_passed": False,
        "validation_feedback": "",
        "retry_count": 0,
        "pr_url": None,
        "messages": [],
        "error": None,
    }

    print("🤖 OSS Contributor Agent starting...\n")
    final_state = graph.invoke(initial_state)  # type: ignore

    print("\n" + "═" * 60)
    if final_state.get("pr_url"):
        print(f"✅ Done!  PR: {final_state['pr_url']}")
    else:
        print("⚠️  Agent finished without creating a PR.")
        if final_state.get("error"):
            print(f"   Reason: {final_state['error']}")


if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    main()
