from fastapi import FastAPI
from typing import Any, Dict, Tuple

from src.reward import compute_reward

app = FastAPI()


class CodeGuardEnv:
    def __init__(self) -> None:
        self.state: Dict[str, Any] = {}
        self.current_step: int = 0
        self.max_steps: int = 50
        self.threshold: float = 0.95
        self.done: bool = False

    def reset(self) -> Dict[str, Any]:
        self.state = {
            "score": 0.0,
            "history": [],
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

        base_score: float = 1.0 if "fix" in action.lower() else 0.0

        reward: float = compute_reward(self.state, action, base_score)

        self.state["score"] = reward
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
