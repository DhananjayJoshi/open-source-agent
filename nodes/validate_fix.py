"""
NODE 5 — Validate fix
"""

from langchain_core.messages import AIMessage, HumanMessage

from llm import get_llm
from state import AgentState


def validate_fix(state: AgentState) -> dict:
    """
    Ask the LLM to review the proposed changes before creating a PR.
    In a real setup this also runs the test suite in a Docker sandbox.
    """
    print("\n✅ [validate_fix] Reviewing fix...")

    if not state["code_changes"]:
        return {
            "validation_passed": False,
            "validation_feedback": "No code changes were generated.",
        }

    changes_text = "\n\n".join(
        f"File: {c['file_path']}\nChange: {c['original_content']} → {c['new_content']}\nReason: {c['explanation']}"
        for c in state["code_changes"]
    )

    issue = state["current_issue"]
    prompt = f"""Review this proposed fix for GitHub issue #{issue["number"]}: "{issue["title"]}"

{changes_text}

Does this fix:
1. Actually address the issue?
2. Introduce no regressions?
3. Follow good coding practices?

Reply with PASS or FAIL, then a brief explanation."""

    llm = get_llm(operation="validate")
    response = llm.invoke([HumanMessage(content=prompt)])
    verdict = response.content.strip()
    passed = verdict.upper().startswith("PASS")

    print(f"   {'🟢 PASS' if passed else '🔴 FAIL'}: {verdict[:80]}")

    return {
        "validation_passed": passed,
        "validation_feedback": verdict,
        "messages": [AIMessage(content=f"Validation: {'PASS' if passed else 'FAIL'}")],
    }
