import re
from profanity_check import predict, predict_prob

from src.actions.database import get_player_by_summoner_name
from src.resources.constants import ONLY_MODS as VALID_SUMMONER_NAME_REGEX
from src.resources.entity import Player
from src.resources.logging_constants import COMMAND_ERROR_SUMMONER_NAME, ERROR_EXISTING_SUMMONER, \
    COMMAND_ERROR_DISPLAY_NAME_LENGTH, COMMAND_ERROR_DISCORD_ID


def validate_summoner_name_and_display_name(summoner_name: str, display_name: str) -> None:
    if not re.search(VALID_SUMMONER_NAME_REGEX, summoner_name):
        raise ValueError(COMMAND_ERROR_SUMMONER_NAME.format(summoner_name))
    if display_name is not None and (len(display_name) < 3 or len(display_name) > 16):
        raise ValueError(COMMAND_ERROR_DISPLAY_NAME_LENGTH)
    if get_player_by_summoner_name(summoner_name) is not None:
        raise ValueError(ERROR_EXISTING_SUMMONER.format(summoner_name))
    c


def validate_discord_id(player:Player, discord_id: int) -> None:
    if player.discord_id != discord_id:
        raise ValueError(COMMAND_ERROR_DISCORD_ID)
