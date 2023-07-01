from objects import Score

import session
import os


def upload_score(score: Score, replay_file: bytes):
    os.makedirs(f"{session.config['folder']}/{score.player.name}", exist_ok=True)

    with open(
        f"{session.config['folder']}/{score.player.name}/{score.filename}", "wb"
    ) as osr:
        osr.write(replay_file)

    session.manager.logger.info(
        f"Replay saved to '{session.config['folder']}/{score.player.name}/{score.filename}'"
    )
