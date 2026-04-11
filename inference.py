import os
import sys
from typing import Any, Dict, List, Optional

from openai import OpenAI


# Required submission variables.
# Defaults are provided only for API_BASE_URL and MODEL_NAME.
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")


# Compatibility fallback. HF_TOKEN remains the primary required variable.
API_KEY = HF_TOKEN or os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")

TASK_NAME = os.getenv("TASK", "easy")
BENCHMARK = os.getenv("BENCHMARK", "codeguard")


def _bootstrap_path() -> None:
    repo_root = os.path.dirname(os.path.abspath(__file__))
    agentbox_root = os.path.join(repo_root, "AgentBox")
    if agentbox_root not in sys.path:
        sys.path.insert(0, agentbox_root)


def _fmt_bool(value: bool) -> str:
    return "true" if value else "false"


def _fmt_error(error: Optional[str]) -> str:
    return "null" if error is None else str(error)


def _clamp_score(value: float) -> float:
    return max(0.0, min(1.0, value))


def main() -> None:
    _bootstrap_path()
    from src.env import CodeGuardEnv

    rewards: List[float] = []
    steps: int = 0
    score: float = 0.0
    success: bool = False

    print(f"[START] task={TASK_NAME} env={BENCHMARK} model={MODEL_NAME}")

    env = None
    try:
        client = None
        init_error: Optional[str] = None
        if API_KEY:
            try:
                client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
            except Exception as exc:
                init_error = str(exc)
        else:
            init_error = "Missing HF_TOKEN (or API_KEY)"

        env = CodeGuardEnv()
        state: Dict[str, Any] = env.reset()
        done = False

        while not done:
            steps += 1

            model_error: Optional[str] = None
            if client is None:
                action = ""
                model_error = init_error
            else:
                try:
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "system", "content": "You are a code-fixing agent."},
                            {"role": "user", "content": str(state)},
                        ],
                        temperature=0.0,
                    )
                    action = (response.choices[0].message.content or "").strip()
                except Exception as exc:
                    action = ""
                    model_error = str(exc)

            next_state, reward, done, info = env.step(action)
            rewards.append(float(reward))

            step_error = model_error or info.get("error")
            print(
                f"[STEP] step={steps} action={action} reward={float(reward):.2f} "
                f"done={_fmt_bool(done)} error={_fmt_error(step_error)}"
            )

            state = next_state
            score = _clamp_score(float(state.get("score", 0.0)))
            if done and float(reward) >= env.threshold:
                success = True

    except Exception:
        success = False
        score = 0.0
    finally:
        rewards_str = ",".join(f"{r:.2f}" for r in rewards) if rewards else "0.00"
        print(
            f"[END] success={_fmt_bool(success)} steps={steps} "
            f"score={score:.2f} rewards={rewards_str}"
        )


if __name__ == "__main__":
    main()