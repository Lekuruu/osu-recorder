from osu.objects import ScoreFrame, Player, Status
from osu.bancho.constants import Mods

from datetime import datetime
from typing import List

import hashlib
import os


class Score:
    def __init__(
        self,
        score_frames: List[ScoreFrame],
        player: Player,
        status: Status,
        passed: bool,
    ) -> None:
        self.player = player
        self.status = status
        self.passed = passed
        self.frames = score_frames
        self.data = self.frames[-1]

    @property
    def checksum(self) -> str:
        frame = self.frames[-1]
        return hashlib.md5(
            f"{frame.max_combo}osu{self.player.name}{self.status.checksum}{frame.total_score}{self.grade}".encode()
        ).hexdigest()

    @property
    def accuracy(self) -> float:
        if self.data.total_hits <= 0:
            return 1.0

        return (
            (self.data.c50 * 50 + self.data.c100 * 100 + self.data.c300 * 300)
            / self.data.total_hits
            * 100
        )

    @property
    def grade(self) -> str:
        num = self.data.c300 / self.data.total_hits
        num2 = self.data.c50 / self.data.total_hits

        if not self.passed:
            return "F"

        if num == 1.0:
            if Mods.Hidden in self.mods or Mods.Flashlight in self.mods:
                return "XH"
            return "X"

        if num > 0.9 and num2 <= 0.01 and self.data.cMiss == 0:
            if Mods.Hidden in self.mods or Mods.Flashlight in self.mods:
                return "SH"
            return "S"

        else:
            if num > 0.8 and self.data.cMiss == 0 or num > 0.9:
                return "A"

            if num > 0.7 and self.data.cMiss == 0 or num > 0.8:
                return "B"

            if num > 0.6:
                return "C"

        return "D"

    @property
    def mods(self) -> List[Mods]:
        return self.status.mods

    @property
    def filename(self) -> str:
        name = f'{self.player.name} - {self.status.text} ({datetime.now().strftime("%Y-%m-%d %H-%M-%S")}) {self.status.mode.name}'

        # Remove invalid characters
        for invalid_char in [".", "..", "<", ">", ":", '"', "/", "\\", "|", "?", "*"]:
            name = name.replace(invalid_char, "")

        return name + ".osr"

    @property
    def filename_safe(self) -> str:
        return f"replay-{self.status.mode.name.lower()}_{self.checksum}.osr"

    @property
    def hp_graph(self) -> str:
        graph = [
            f"{frame.time}|{min(1.0, frame.current_hp / 200)}" for frame in self.frames
        ]
        return ",".join(graph)

    def save_to_file(self, replay_file: bytes) -> None:
        import session

        os.makedirs(f"{session.config['folder']}/{self.player.name}", exist_ok=True)

        with open(
            f"{session.config['folder']}/{self.player.name}/{self.filename}", "wb"
        ) as osr:
            osr.write(replay_file)

        session.manager.logger.info(
            f"Replay saved to '{session.config['folder']}/{self.player.name}/{self.filename}'"
        )
