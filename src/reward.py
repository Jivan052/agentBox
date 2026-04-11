from typing import Dict


MIN_REWARD: float = -2.5
MAX_REWARD: float = 1.0


def _is_destructive(action: str) -> bool:
	destructive_keywords = ["delete", "remove", "drop"]
	critical_targets = ["function", "class"]

	action_lower = action.lower()
	return any(k in action_lower for k in destructive_keywords) and any(
		t in action_lower for t in critical_targets
	)


def compute_reward(state: Dict, action: str, base_score: float) -> float:
	reward = base_score
	reward -= 0.02

	if _is_destructive(action):
		reward -= 2.0

	reward = max(MIN_REWARD, min(MAX_REWARD, reward))
	return round(reward, 2)
