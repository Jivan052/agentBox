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


def main() -> None:
    success: bool = False
    rewards: List[float] = []
    step_count: int = 0

    try:
        # --- ENV VARS ---
        hf_token: str = _get_env_var("HF_TOKEN", required=True)
        base_url: str = _get_env_var("BASE_URL", "https://api.openai.com/v1")
        model: str = _get_env_var("MODEL", "gpt-4.1-mini")
        task_name: str = _get_env_var("TASK", "easy")

        # --- CLIENT INIT ---
        client = OpenAI(base_url=base_url, api_key=hf_token)

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

            # Success condition
            if done and reward >= env.threshold:
                success = True

        # --- END LOG ---
        reward_str = ",".join(f"{r:.2f}" for r in rewards)
        print(f"[END] success={_format_bool(success)} steps={step_count} rewards={reward_str}")

    except Exception as e:
        # Ensure END always prints
        _ = str(e)
        reward_str = ",".join(f"{r:.2f}" for r in rewards) if rewards else "0.00"
        print(f"[END] success=false steps={step_count} rewards={reward_str}")


if __name__ == "__main__":
    main()

