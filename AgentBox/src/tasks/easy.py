from typing import Dict
import ast


def get_task() -> Dict:
    return {
        "name": "lint_fix",
        "description": "Fix syntax errors in the given Python code.",
    }


def grade(candidate_code: str) -> float:
    """
    Deterministic grader:
    - Returns 1.0 if code parses successfully
    - Returns 0.0 if syntax error occurs
    """
    try:
        ast.parse(candidate_code)
        return 1.0
    except SyntaxError:
        return 0.0
