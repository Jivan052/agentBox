from typing import Dict
import ast


MIN_TASK_SCORE = 0.01
MAX_TASK_SCORE = 0.99


def get_task() -> Dict:
	return {
		"name": "refactor_types",
		"description": "Refactor code and add type hints.",
		"grader": "grade",
		"score_range": [MIN_TASK_SCORE, MAX_TASK_SCORE],
	}


def _count_type_hints(tree: ast.AST) -> int:
	count = 0
	for node in ast.walk(tree):
		if isinstance(node, ast.AnnAssign):
			count += 1
		elif isinstance(node, ast.FunctionDef):
			if node.returns is not None:
				count += 1
			for arg in node.args.args:
				if arg.annotation is not None:
					count += 1
	return count


def _count_defs(tree: ast.AST) -> int:
	return sum(isinstance(node, (ast.FunctionDef, ast.ClassDef)) for node in ast.walk(tree))


def grade(candidate_code: str) -> float:
	try:
		tree = ast.parse(candidate_code)
	except SyntaxError:
		return MIN_TASK_SCORE

	score = 0.0
	if _count_defs(tree) > 0:
		score += 0.5
	if _count_type_hints(tree) > 0:
		score += 0.5

	score = round(score, 2)
	return max(MIN_TASK_SCORE, min(MAX_TASK_SCORE, score))
