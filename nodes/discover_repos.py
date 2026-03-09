"""
NODE 1 — Discover repos
"""

from langchain_core.messages import AIMessage, HumanMessage

from llm import get_llm
from state import AgentState, RepoInfo, RepoList


def load_prompt() -> str:
    """Load the system prompt from the markdown file."""
    file_path = "opensource-contribution-system-prompt.md"
    try:
        with open(file_path, "r") as file:
            contents = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return ""
    except PermissionError:
        print(f"Error: Permission denied for '{file_path}'.")
        return ""
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return ""

    return contents


def discover_repos(state: AgentState) -> dict:
    """Ask the LLM to propose a list of candidate repositories."""
    print(f"\n🔍 [discover_repos] Querying LLM for '{state['topic']}' repos...")
    llm = get_llm(operation="discover")
    system_prompt = load_prompt()
    structured_llm = llm.with_structured_output(RepoList)

    # Combine system prompt and user request into a single message
    # (some models like Gemma don't support separate system messages)
    combined_prompt = f"{system_prompt}\n\nFind me 5 beginner-friendly {state['language']} repos on the topic of {state['topic']}."

    response = structured_llm.invoke(
        [
            HumanMessage(content=combined_prompt),
        ]
    )

    repos: list[RepoInfo] = response.repos  # type: ignore
    for repo in repos:
        print(f"   ⭐ {repo['full_name']} ({repo['stars']} stars)")

    return {
        "discovered_repos": repos,
        "messages": [
            AIMessage(
                content=f"LLM suggested {len(repos)} repos for topic '{state['topic']}'"
            )
        ],
    }
