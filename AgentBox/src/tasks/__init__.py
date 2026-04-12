from typing import Callable, Dict

from .easy import get_task as get_easy_task, grade as easy_grade
from .medium import get_task as get_medium_task, grade as medium_grade
from .hard import get_task as get_hard_task, grade as hard_grade


TASKS: Dict[str, Dict] = {
	"easy": get_easy_task(),
	"medium": get_medium_task(),
	"hard": get_hard_task(),
}

GRADERS: Dict[str, Callable[[str], float]] = {
	"easy": easy_grade,
	"medium": medium_grade,
	"hard": hard_grade,
}

# Canonical easy->medium->hard ordered tasks for validator discovery.
TASK_SEQUENCE = ["easy", "medium", "hard"]

# Explicit task/grader pairs with callable graders.
TASKS_WITH_GRADERS = [
	{
		"id": key,
		"difficulty": TASKS[key].get("difficulty", key),
		"task": TASKS[key],
		"grader": GRADERS[key],
	}
	for key in TASK_SEQUENCE
]


def list_tasks_with_graders():
	return TASKS_WITH_GRADERS

