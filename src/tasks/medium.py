from typing import Dict
import ast


UNSAFE_FUNCTIONS = {"eval", "exec", "compile", "__import__"}
MIN_TASK_SCORE = 0.01
MAX_TASK_SCORE = 0.99


def get_task() -> Dict:
	return {
		"id": "medium",
		"difficulty": "medium",
		"name": "vuln_patch",
		"objective": "Remove unsafe calls while preserving function structure.",
		"description": "Remove unsafe function usage while preserving functionality.",
		"grader_name": "grade",
		"score_range": [MIN_TASK_SCORE, MAX_TASK_SCORE],
	}


class UnsafeCallVisitor(ast.NodeVisitor):
	def __init__(self) -> None:
		self.unsafe_calls = 0

	def visit_Call(self, node: ast.Call) -> None:
		if isinstance(node.func, ast.Name) and node.func.id in UNSAFE_FUNCTIONS:
			self.unsafe_calls += 1
		self.generic_visit(node)


def _has_function_def(tree: ast.AST) -> bool:
	return any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))


def grade(candidate_code: str) -> float:
	try:
		tree = ast.parse(candidate_code)
	except SyntaxError:
		return MIN_TASK_SCORE

	visitor = UnsafeCallVisitor()
	visitor.visit(tree)

	score = 0.0
	if visitor.unsafe_calls == 0:
		score += 0.7
	if _has_function_def(tree):
		score += 0.3

	score = round(score, 2)
	return max(MIN_TASK_SCORE, min(MAX_TASK_SCORE, score))
