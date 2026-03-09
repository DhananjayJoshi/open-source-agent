"""
NODE 4 — Fix issue
"""

from typing import Optional

from langchain_core.messages import AIMessage, HumanMessage

from llm import get_llm
from state import AgentState, CodeChange


def _extract_section(text: str, start_marker: str, end_marker: Optional[str]) -> str:
    """Extract text between two markers."""
    start = text.find(start_marker)
    if start == -1:
        return ""
    start += len(start_marker)
    if end_marker:
        end = text.find(end_marker, start)
        return text[start:end].strip() if end != -1 else text[start:].strip()
    return text[start:].strip()


def fix_issue(state: AgentState) -> dict:
    """
    Use the LLM to generate a code fix for the selected issue.
    On retries, validation_feedback is included so the model can self-correct.
    """
    issue = state["current_issue"]
    retry = state["retry_count"]
    feedback = state.get("validation_feedback", "")

    print(f"\n🔧 [fix_issue] Generating fix (attempt {retry + 1})...")

    retry_context = (
        f"\n\nPrevious attempt failed validation:\n{feedback}" if feedback else ""
    )

    prompt = f"""You are an expert open-source contributor fixing a GitHub issue.

Repository: {issue["repo"]["full_name"]}
Issue #{issue["number"]}: {issue["title"]}

Issue description:
{issue["body"][:2000]}
{retry_context}

Provide a concrete fix. For each file you change, output a block in this exact format:

FILE: <relative/path/to/file.py>
ORIGINAL:
<the exact lines you are replacing>
NEW:
<the replacement lines>
EXPLANATION:
<one-sentence reason for this change>
---

Be minimal — change only what is necessary to fix the issue."""

    llm = get_llm(operation="fix")
    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content

    # ────────────────────────────────────────────────────────────────────────
    # Parse LLM output into CodeChange objects
    # ────────────────────────────────────────────────────────────────────────
    changes: list[CodeChange] = []
    for block in raw.split("---"):
        if "FILE:" not in block:
            continue
        lines = block.strip().splitlines()
        try:
            file_path = next(
                l.split("FILE:")[-1].strip() for l in lines if l.startswith("FILE:")
            )
            original = _extract_section(block, "ORIGINAL:", "NEW:")
            new_content = _extract_section(block, "NEW:", "EXPLANATION:")
            explanation = _extract_section(block, "EXPLANATION:", None)
            changes.append(
                CodeChange(
                    file_path=file_path,
                    original_content=original,
                    new_content=new_content,
                    explanation=explanation,
                )
            )
        except (StopIteration, ValueError):
            continue

    print(f"   📝 Generated {len(changes)} file change(s)")

    return {
        "code_changes": changes,
        "fix_explanation": raw,
        "retry_count": retry + 1,
        "messages": [AIMessage(content=f"Generated fix with {len(changes)} change(s)")],
    }
