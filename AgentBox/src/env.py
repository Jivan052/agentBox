from fastapi import FastAPI
from typing import Any, Dict, Tuple
import os

from src.reward import compute_reward
from src.tasks import GRADERS, TASKS

app = FastAPI()


class CodeGuardEnv:
    def __init__(self) -> None:
        self.state: Dict[str, Any] = {}
        self.current_step: int = 0
        self.max_steps: int = 50
        self.threshold: float = 0.95
        self.done: bool = False
        requested_task = os.getenv("TASK", "easy").strip().lower()
        self.task_key: str = requested_task if requested_task in GRADERS else "easy"

    def _get_task_score(self, action: str) -> float:
        grader = GRADERS[self.task_key]
        base_score = float(grader(action))
        # Strict score interval for validator compatibility.
        return max(0.01, min(0.99, base_score))

    def _get_all_task_scores(self, action: str) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for key, grader in GRADERS.items():
            score = float(grader(action))
            scores[key] = max(0.01, min(0.99, score))
        return scores

    def reset(self) -> Dict[str, Any]:
        self.state = {
            "score": 0.01,
            "history": [],
            "task": TASKS[self.task_key],
            "tasks": list(TASKS.values()),
            "task_scores": {k: 0.01 for k in GRADERS.keys()},
        }
        self.current_step = 0
        self.done = False
        return self.state

    def _is_valid_action(self, action: str) -> bool:
        if not isinstance(action, str):
            return False
        if len(action.strip()) == 0:
            return False
        if len(action) > 1000:
            return False
        return True

    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        if self.done:
            return self.state, 0.0, True, {"error": "episode_done"}

        self.current_step += 1

        info: Dict[str, Any] = {"error": None}

        if not self._is_valid_action(action):
            self.done = True
            return self.state, -1.0, True, {"error": "invalid_action"}

        base_score: float = self._get_task_score(action)

        reward: float = compute_reward(self.state, action, base_score)

        self.state["score"] = max(0.01, min(0.99, base_score))
        self.state["task_scores"] = self._get_all_task_scores(action)
        self.state["history"].append(
            {
                "step": self.current_step,
                "action": action,
                "reward": reward,
            }
        )

        if reward <= -2.0:
            self.done = True
        elif reward >= self.threshold:
            self.done = True
        elif self.current_step >= self.max_steps:
            self.done = True

        return self.state, reward, self.done, info


# --- FastAPI Routes ---

env_instance = CodeGuardEnv()


@app.get("/")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/reset")
def reset() -> Dict[str, Any]:
    return env_instance.reset()


@app.post("/step")
def step(action: str) -> Dict[str, Any]:
    state, reward, done, info = env_instance.step(action)
    return {
        "state": state,
        "reward": reward,
        "done": done,
        "info": info,
    }


@app.get("/state")
def state() -> Dict[str, Any]:
    return env_instance.state
