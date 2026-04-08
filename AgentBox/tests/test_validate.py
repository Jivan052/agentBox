import re

from src.reward import compute_reward
from src.tasks.easy import grade as easy_grade
from src.tasks.medium import grade as medium_grade
from src.tasks.hard import grade as hard_grade


def test_easy_grader() -> None:
    assert easy_grade("x=1") == 1.0
    assert easy_grade("x=") == 0.0


def test_medium_grader() -> None:
    safe_code = "def f(): return 1"
    unsafe_code = "def f(): eval('2+2')"

    assert medium_grade(safe_code) >= 0.7
    assert medium_grade(unsafe_code) < 1.0


def test_hard_grader() -> None:
    code_with_types = "def f(x: int) -> int: return x"
    code_without_types = "def f(x): return x"

    assert hard_grade(code_with_types) > hard_grade(code_without_types)


def test_reward_bounds() -> None:
    state = {}

    r = compute_reward(state, "fix code", 1.0)
    assert -2.5 <= r <= 1.0

    r = compute_reward(state, "delete function", 0.0)
    assert r <= -2.0


def test_inference_format() -> None:
    step_line = "[STEP] step=1 action=fix reward=0.50 done=false error=null"

    pattern = r"^\[STEP\] step=\d+ action=.* reward=-?\d+\.\d{2} done=(true|false) error=(null|.*)$"
    assert re.match(pattern, step_line)
