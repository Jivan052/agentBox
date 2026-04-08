from typing import Dict


MIN_REWARD: float = -2.5
MAX_REWARD: float = 1.0


def _is_destructive(action: str) -> bool:
    """
    Detect destructive actions such as removing core structures.
    Simple deterministic heuristic.
    """
    destructive_keywords = ["delete", "remove", "drop"]
    critical_targets = ["function", "class"]

    action_lower = action.lower()

    return any(k in action_lower for k in destructive_keywords) and any(
        t in action_lower for t in critical_targets
    )


def compute_reward(state: Dict, action: str, base_score: float) -> float:
    """
    Reward logic:
    + base_score (from grader)
    - 0.02 step penalty
    - 2.0 destructive penalty (if applicable)

    Final reward clipped to [-2.5, 1.0]
    """
    reward = base_score

    # Step penalty (loop prevention)
    reward -= 0.02

    # Destructive penalty
    if _is_destructive(action):
        reward -= 2.0

    # Clip bounds
    reward = max(MIN_REWARD, min(MAX_REWARD, reward))

    return round(reward, 2)
