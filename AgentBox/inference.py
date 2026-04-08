import os
from typing import Any, Dict, List, Optional

from openai import OpenAI

from src.env import CodeGuardEnv


def _get_env_var(name: str, default: Optional[str] = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value or ""


def _format_bool(value: bool) -> str:
    return "true" if value else "false"


def _safe_str(value: Optional[str]) -> str:
    if value is None:
        return "null"
    return str(value)


def _get_api_key() -> str:
    # Submission-required variable first, with compatibility fallbacks.
    for name in ("HF_TOKEN", "API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY"):
        value = os.getenv(name)
        if value:
            return value
    raise ValueError(
        "Missing API key. Set one of: HF_TOKEN, API_KEY, GEMINI_API_KEY, OPENAI_API_KEY"
    )


def _resolve_base_url(api_key: str) -> str:
    explicit_base_url = os.getenv("API_BASE_URL") or os.getenv("BASE_URL")
    if explicit_base_url:
        return explicit_base_url

    # Default should reflect active inference setup for submission.
    # Keep provider-aware fallback behavior.
    if api_key.startswith("hf_"):
        return "https://router.huggingface.co/v1"
    if api_key.startswith("AIza"):
        return "https://generativelanguage.googleapis.com/v1beta/openai"
    return "https://router.huggingface.co/v1"


def _resolve_model(base_url: str) -> str:
    explicit_model = os.getenv("MODEL_NAME") or os.getenv("MODEL")
    if explicit_model:
        return explicit_model

    if "router.huggingface.co" in base_url:
        return "Qwen/Qwen2.5-72B-Instruct"
    if "generativelanguage.googleapis.com" in base_url:
        return "gemini-1.5-flash"
    return "gpt-4.1-mini"


def _clamp_score(value: float) -> float:
    return max(0.0, min(1.0, value))


def main() -> None:
    success: bool = False
    rewards: List[float] = []
    step_count: int = 0
    score: float = 0.0

    try:
        # --- ENV VARS ---
        api_key: str = _get_api_key()
        base_url: str = _resolve_base_url(api_key)
        model: str = _resolve_model(base_url)
        task_name: str = _get_env_var("TASK", "easy")

        # --- CLIENT INIT ---
        client = OpenAI(base_url=base_url, api_key=api_key)

        # --- ENV INIT ---
        env = CodeGuardEnv()
        state: Dict[str, Any] = env.reset()

        # --- START LOG ---
        print(f"[START] task={task_name} env=codeguard model={model}")

        done: bool = False

        while not done:
            step_count += 1

            # --- LLM CALL ---
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a code-fixing agent."},
                        {"role": "user", "content": str(state)},
                    ],
                    temperature=0.0,
                )
                action: str = response.choices[0].message.content.strip()
                error_msg: Optional[str] = None
            except Exception as e:
                action = ""
                error_msg = str(e)

            # --- ENV STEP ---
            next_state, reward, done, info = env.step(action)

            rewards.append(reward)

            # Merge error sources
            error_output: Optional[str] = error_msg or info.get("error")

            # --- STEP LOG ---
            print(
                f"[STEP] step={step_count} action={action} "
                f"reward={reward:.2f} done={_format_bool(done)} "
                f"error={_safe_str(error_output)}"
            )

            state = next_state

            # Keep score in [0, 1] for validator compatibility.
            score = _clamp_score(float(state.get("score", 0.0)))

            # Success condition
            if done and reward >= env.threshold:
                success = True

        # --- END LOG ---
        reward_str = ",".join(f"{r:.2f}" for r in rewards)
        print(
            f"[END] success={_format_bool(success)} steps={step_count} "
            f"score={score:.2f} rewards={reward_str}"
        )

    except Exception as e:
        # Ensure END always prints
        _ = str(e)
        reward_str = ",".join(f"{r:.2f}" for r in rewards) if rewards else "0.00"
        print(f"[END] success=false steps={step_count} score=0.00 rewards={reward_str}")


if __name__ == "__main__":
    main()

