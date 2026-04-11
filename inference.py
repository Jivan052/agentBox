import os
import sys


def _bootstrap_path() -> None:
    repo_root = os.path.dirname(os.path.abspath(__file__))
    agentbox_root = os.path.join(repo_root, "AgentBox")
    if agentbox_root not in sys.path:
        sys.path.insert(0, agentbox_root)


def main() -> None:
    _bootstrap_path()
    from inference import main as agentbox_main

    agentbox_main()


if __name__ == "__main__":
    main()