from typing import Optional, Tuple, List
from datetime import datetime, timezone
from objects import Score
from copy import copy

from osu.objects import ReplayFrame, ScoreFrame
from osu.bancho.constants import ReplayAction
from osu.bancho.streams import StreamOut
from osu.objects import Player, Status
from osu import Game

import logging
import lzma

MIN_REPLAY_SIZE = 120


class Replay:
    def __init__(self, manager: "ReplayManager") -> None:
        self.game = manager.game
        self.manager = manager

        self.score_frames: List[ScoreFrame] = []
        self.frames: List[ReplayFrame] = []
        self.seed = 0

        self.logger = logging.getLogger("replay-manager")
        self.completed = False
        self.passed = False

    @property
    def player(self) -> Optional[Player]:
        return self.manager.spectating

    @property
    def ticks(self) -> int:
        return int(
            (
                datetime.now(timezone.utc) - datetime(1, 1, 1, tzinfo=timezone.utc)
            ).total_seconds()
            * 10_000_000
        )

    @property
    def replay_string(self) -> str:
        previous_frame = ReplayFrame([], 0, 0.0, 0.0)
        frames = []

        for frame in self.frames:
            frames.append(
                "|".join(
                    [
                        str(frame.time - previous_frame.time),
                        str(frame.x),
                        str(frame.y),
                        str(frame.button_state.value),
                    ]
                )
            )
            previous_frame = frame

        # Append "seed"
        frames.append(f"-12345|0|0|{self.seed}")

        return ",".join(frames)

    @property
    def replay_compressed(self) -> bytes:
        compressed = lzma.compress(self.replay_string.encode(), lzma.FORMAT_ALONE)
        stream = StreamOut()
        stream.s32(len(compressed))
        stream.write(compressed)
        return stream.get()

    def get_replay(self, score: Score) -> bytes:
        replay = StreamOut()
        frame = score.frames[-1]

        header = StreamOut()
        header.u8(score.status.mode.value)
        header.s32(round(self.game.version_number))
        header.string(score.status.checksum)
        header.string(score.player.name)
        header.string(score.checksum)
        header.u16(frame.c300)
        header.u16(frame.c100)
        header.u16(frame.c50)
        header.u16(frame.cGeki)
        header.u16(frame.cKatu)
        header.u16(frame.cMiss)
        header.s32(frame.total_score)
        header.u16(frame.max_combo)
        header.bool(frame.perfect)
        header.s32(score.status.mods.value)
        header.string(score.hp_graph)
        header.s64(self.ticks)

        replay.write(header.get())
        replay.write(self.replay_compressed)
        replay.s64(0)  # score_id

        return replay.get()

    def create(self) -> Optional[Tuple[Score, bytes]]:
        self.logger.name = f"replay-manager-{self.player.name}"

        self.logger.info("Creating replay...")

        if len(self.frames) <= MIN_REPLAY_SIZE:
            self.logger.warning(
                f"Replay save failed: Replay too short ({len(self.frames)})"
            )
            self.reset()
            return

        if not self.score_frames:
            self.logger.warning("Replay save failed: No score frames found")
            self.reset()
            return

        if self.score_frames[-1].total_hits <= 0:
            self.logger.warning("Replay save failed: Total hits <= 0")
            return

        status: Status = self.manager.current_status

        if not status.checksum:
            self.logger.warning("Replay save failed: Missing status")
            self.reset()
            return

        score = Score(self.score_frames, self.player, status, self.passed)
        replay_file = self.get_replay(score)

        self.game.tasks.executor.submit(score.save_to_file, replay_file)
        self.reset()

        return score, replay_file

    def reset(self) -> None:
        self.score_frames = []
        self.frames = []
        self.seed = 0


class ReplayManager:
    def __init__(self, game: Game) -> None:
        self.last_action = ReplayAction.SongSelect
        self.game = game

        self.current_status = Status()
        self.replay = Replay(self)
        self.logger = logging.getLogger("replay-manager")

    @property
    def spectating(self) -> Optional[Player]:
        return self.game.bancho.spectating

    def handle_frames(
        self,
        frames: List[ReplayFrame],
        action: ReplayAction,
        extra: int,
        score_frame: Optional[ScoreFrame],
    ) -> None:
        if not self.spectating:
            self.logger.warning("No target was found for spectating!")
            return

        if action == ReplayAction.Standard:
            self.replay.seed = extra

        elif action == ReplayAction.NewSong:
            if not self.replay.completed:
                self.replay.passed = False
                self.replay.create()

            self.replay.reset()
            self.replay.completed = False

            self.game.bancho.request_stats([self.spectating.id])
            self.logger.info(
                f"{self.spectating} selected new song: {self.spectating.status.text} (https://osu.ppy.sh/b/{self.spectating.status.beatmap_id})."
            )

            if self.spectating.status.checksum:
                # Set new map as current status
                self.current_status = copy(self.spectating.status)

        elif action == ReplayAction.Skip:
            self.game.bancho.request_stats([self.spectating.id])
            self.logger.info(f"{self.spectating} skipped.")

        elif action == ReplayAction.Completion:
            if self.last_action != action:
                self.game.bancho.request_stats([self.spectating.id])
                self.logger.info(f"{self.spectating} passed.")
                self.replay.passed = True
                self.replay.completed = True
                self.replay.create()

        elif action == ReplayAction.Fail:
            if self.last_action != action:
                self.game.bancho.request_stats([self.spectating.id])
                self.logger.info(f"{self.spectating} failed.")
                self.replay.completed = True
                self.replay.create()

        elif action == ReplayAction.Pause:
            self.logger.info(f"{self.spectating} paused.")
            self.game.bancho.request_stats([self.spectating.id])

        elif action == ReplayAction.Unpause:
            self.logger.info(f"{self.spectating} unpaused.")
            self.game.bancho.request_stats([self.spectating.id])

        elif action == ReplayAction.SongSelect:
            self.logger.info(f"{self.spectating} is selecting new song...")

            if not self.replay.completed:
                self.replay.passed = False
                self.replay.create()

        elif action == ReplayAction.WatchingOther:
            self.game.bancho.request_stats([self.spectating.id])
            self.logger.warning(
                f"{self.spectating} is currently spectating another player."
            )
            return

        if not self.current_status.checksum and self.spectating.status.checksum:
            # Current status has no valid beatmap
            self.current_status = copy(self.spectating.status)

        self.replay.frames.extend(frames)

        if score_frame:
            self.replay.score_frames.append(score_frame)

        self.last_action = action
