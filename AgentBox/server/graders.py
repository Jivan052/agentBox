import ast
from typing import Any


def _extract_text(payload: Any) -> str:
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict):
        for key in ("candidate", "code", "action", "text", "output"):
            value = payload.get(key)
            if isinstance(value, str):
                return value
        return str(payload)
    return str(payload)


class EasyGrader:
    """Easy: syntax/lint style signal."""

    def grade(self, payload: Any) -> float:
        text = _extract_text(payload)
        if not text.strip():
            return 0.10
        try:
            ast.parse(text)
            return 0.90
        except SyntaxError:
            return 0.20


class MediumGrader:
    """Medium: safety patch signal."""

    _unsafe = ("eval(", "exec(", "compile(", "__import__(")

    def grade(self, payload: Any) -> float:
        text = _extract_text(payload)
        if not text.strip():
            return 0.20
        lower = text.lower()
        score = 0.20
        if all(tok not in lower for tok in self._unsafe):
            score += 0.45
        if "def " in lower:
            score += 0.25
        return max(0.01, min(0.99, round(score, 2)))


class HardGrader:
    """Hard: structure + typing signal."""

    def grade(self, payload: Any) -> float:
        text = _extract_text(payload)
        if not text.strip():
            return 0.30
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return 0.25

        score = 0.25
        has_def_or_class = any(
            isinstance(node, (ast.FunctionDef, ast.ClassDef)) for node in ast.walk(tree)
        )
        if has_def_or_class:
            score += 0.30

        has_annotations = False
        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign):
                has_annotations = True
                break
            if isinstance(node, ast.FunctionDef):
                if node.returns is not None:
                    has_annotations = True
                    break
                if any(arg.annotation is not None for arg in node.args.args):
                    has_annotations = True
                    break
        if has_annotations:
            score += 0.35

        return max(0.01, min(0.99, round(score, 2)))
