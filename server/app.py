from AgentBox.server.app import app, main as agentbox_main


def main(host: str = "0.0.0.0", port: int = 8000):
    return agentbox_main(host=host, port=port)


if __name__ == "__main__":
    main()