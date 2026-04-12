from typing import Dict
import ast


MIN_TASK_SCORE = 0.01
MAX_TASK_SCORE = 0.99


def get_task() -> Dict:
    return {
        "id": "easy",
        "difficulty": "easy",
        "name": "lint_fix",
        "objective": "Fix syntax errors so the candidate code parses successfully.",
        "description": "Fix syntax errors in the given Python code.",
        "grader_name": "grade",
        "score_range": [MIN_TASK_SCORE, MAX_TASK_SCORE],
    }


def grade(candidate_code: str) -> float:
    """
    Deterministic grader:
    - Returns a strict in-range score for valid parse/syntax error
    - Output is always in (0, 1)
    """
    try:
        ast.parse(candidate_code)
        return MAX_TASK_SCORE
    except SyntaxError:
        return MIN_TASK_SCORE
