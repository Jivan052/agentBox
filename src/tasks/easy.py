from typing import Dict
import ast


MIN_TASK_SCORE = 0.01
MAX_TASK_SCORE = 0.99


def get_task() -> Dict:
	return {
		"name": "lint_fix",
		"description": "Fix syntax errors in the given Python code.",
		"grader": "grade",
		"score_range": [MIN_TASK_SCORE, MAX_TASK_SCORE],
	}


def grade(candidate_code: str) -> float:
	try:
		ast.parse(candidate_code)
		return MAX_TASK_SCORE
	except SyntaxError:
		return MIN_TASK_SCORE
