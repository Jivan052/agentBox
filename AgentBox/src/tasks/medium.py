from typing import Dict
import ast


UNSAFE_FUNCTIONS = {"eval", "exec", "compile", "__import__"}


def get_task() -> Dict:
    return {
        "name": "vuln_patch",
        "description": "Remove unsafe function usage while preserving functionality.",
    }


class UnsafeCallVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.unsafe_calls = 0

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            if node.func.id in UNSAFE_FUNCTIONS:
                self.unsafe_calls += 1
        self.generic_visit(node)


def _has_function_def(tree: ast.AST) -> bool:
    return any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))


def grade(candidate_code: str) -> float:
    """
    Score breakdown:
    - No unsafe calls → +0.7
    - Function structure preserved → +0.3
    """
    try:
        tree = ast.parse(candidate_code)
    except SyntaxError:
        return 0.0

    visitor = UnsafeCallVisitor()
    visitor.visit(tree)

    score = 0.0

    if visitor.unsafe_calls == 0:
        score += 0.7

    if _has_function_def(tree):
        score += 0.3

    return round(score, 2)
