from osu.bancho.constants import ServerPackets
from osu.objects import Player

import session


@session.game.events.register(ServerPackets.USER_PRESENCE, threaded=True)
def user_presence(player: Player):
    if session.game.bancho.spectating:
        return

    if session.config["id"] != player.id:
        return

    session.logger.info(f"Found player: {player.name}")

    session.game.bancho.start_spectating(player)

    session.logger.info(f"{player.name} is {player.status}")


@session.game.events.register(ServerPackets.USER_LOGOUT, threaded=True)
def logout(player: Player):
    if player.id == session.config["id"]:
        session.logger.warning(f"{player} is offline.")
        session.game.bancho.exit()
        exit(0)


@session.game.events.register(ServerPackets.SPECTATE_FRAMES, threaded=True)
def frames(action, frames, score_frame, extra):
    session.manager.handle_frames(frames, action, extra, score_frame)


@session.game.events.register(ServerPackets.USER_ID, threaded=True)
def request_user(response: int):
    if response <= 0:
        return

    # Request target user presence when logged in
    session.game.bancho.request_presence([session.config["id"]])
