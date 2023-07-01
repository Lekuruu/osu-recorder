from replays import ReplayManager
from typing import Optional
from osu import Game

import logging

game: Optional[Game] = None
config: Optional[dict] = None
manager: Optional[ReplayManager] = None

logger = logging.getLogger("recorder")
