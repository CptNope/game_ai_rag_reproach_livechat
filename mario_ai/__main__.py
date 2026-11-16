"""Start the dashboard and the AI player: python -m mario_ai"""

import threading

from .agent import Agent
from .config import Config
from .dashboard import create_app
from .session import Session


def main() -> None:
    config = Config()
    session = Session()
    agent = Agent(config, session)
    threading.Thread(target=agent.run, name="mario-ai", daemon=True).start()
    app = create_app(agent)
    print("Dashboard: http://%s:%d" % (config.dashboard_host, config.dashboard_port))
    app.run(host=config.dashboard_host, port=config.dashboard_port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
