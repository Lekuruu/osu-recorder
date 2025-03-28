from replays import ReplayManager
from typing import Optional
from osu import Game

import importlib
import argparse
import logging
import session
import os

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] - <%(name)s> %(levelname)s: %(message)s"
)


def load_config() -> Optional[dict]:
    parser = argparse.ArgumentParser(
        prog="osu!recorder", description="Spectate and record replay files."
    )

    parser.add_argument(
        "<id>", help="Id of the player you want to spectate"
    )
    parser.add_argument(
        "<username>", help="Your bancho username"
    )
    parser.add_argument(
        "<password>", help="Your bancho password"
    )
    parser.add_argument(
        "--tourney",
        help="Allow multiple clients to connect at once.",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--out", default="replays", help="Specify folder where replays get stored"
    )
    parser.add_argument(
        "--server", default="ppy.sh", help="Specify a private server to use"
    )

    args = parser.parse_args()
    dict = args.__dict__

    return {
        "id": int(dict["<id>"]),
        "username": dict["<username>"],
        "password": dict["<password>"],
        "tourney": dict["tourney"],
        "folder": os.path.abspath(dict["out"]),
        "server": dict["server"],
    }


def main():
    session.config = load_config()
    os.makedirs(session.config["folder"], exist_ok=True)

    session.game = Game(
        session.config["username"],
        session.config["password"],
        server=session.config["server"],
        tournament=session.config["tourney"],
        disable_chat_logging=True,
    )

    session.manager = ReplayManager(session.game)
    session.logger.info("Loading events...")
    importlib.import_module("events")
    session.game.run()


if __name__ == "__main__":
    main()
