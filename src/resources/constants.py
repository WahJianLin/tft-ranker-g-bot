from enum import Enum


class RiotTiersEnum(Enum):
    IRON = 100000000
    BRONZE = 200000000
    SILVER = 300000000
    GOLD = 400000000
    PLATINUM = 500000000
    EMERALD = 600000000
    DIAMOND = 700000000
    MASTER = 800000000
    GRANDMASTER = 900000000
    CHALLENGER = 1000000000


class RiotRanksEnum(Enum):
    IV = 100000
    III = 200000
    II = 300000
    I = 400000


class ServerLocationEnum(Enum):
    BR = 'br'
    EUNE = 'eune'
    EUW = 'euw'
    JP = 'jp'
    KR = 'kr'
    LAN = 'lan'
    LAS = 'las'
    ME = 'me'
    NA = 'na'
    OCE = 'oce'
    RU = 'ru'
    SEA = 'sea'
    TR = 'tr'
    TW = 'tw'
    VN = 'vn'


REGION_MAP = {
    ServerLocationEnum.BR: 'americas',
    ServerLocationEnum.EUNE: 'europe',
    ServerLocationEnum.EUW: 'europe',
    ServerLocationEnum.JP: 'asia',
    ServerLocationEnum.KR: 'asia',
    ServerLocationEnum.LAN: 'americas',
    ServerLocationEnum.LAS: 'americas',
    ServerLocationEnum.ME: 'europe',
    ServerLocationEnum.NA: 'americas',
    ServerLocationEnum.OCE: 'asia',
    ServerLocationEnum.RU: 'europe',
    ServerLocationEnum.SEA: 'asia',
    ServerLocationEnum.TR: 'europe',
    ServerLocationEnum.TW: 'asia',
    ServerLocationEnum.VN: 'asia',
}

SERVER_NAME_MAP = {
    ServerLocationEnum.BR: 'br1',
    ServerLocationEnum.EUNE: 'eun1',
    ServerLocationEnum.EUW: 'euw1',
    ServerLocationEnum.JP: 'jp1',
    ServerLocationEnum.KR: 'kr',
    ServerLocationEnum.LAN: 'la1',
    ServerLocationEnum.LAS: 'la2',
    ServerLocationEnum.ME: 'me1',
    ServerLocationEnum.NA: 'na1',
    ServerLocationEnum.OCE: 'oc1',
    ServerLocationEnum.RU: 'ru',
    ServerLocationEnum.SEA: 'sg2',
    ServerLocationEnum.TR: 'tr1',
    ServerLocationEnum.TW: 'tw2',
    ServerLocationEnum.VN: 'vn2',
}

RANKED_QUEUE_TYPE: str = 'RANKED_TFT'

# CONSTANTS names
SUMMONER_ID_JSON_VAL: str = 'summonerId'
SUMMONER_NAME_JSON_VAL: str = 'summonerName'
SERVER_JSON_VAL: str = 'server'
DISPLAY_NAME_JSON_VAL: str = 'displayName'
TIER: str = 'tier'
RANK: str = 'rank'
LEAGUE_POINTS: str = 'leaguePoints'
TFT_RANK_VALUE: str = 'tft_rank_value'
TFT_RANK_TITLE: str = 'tft_rank_title'
QUEUE_TYPE: str = 'queueType'
SUMMONER_NAME: str \
    = 'summoner_name'
DISPLAY_NAME: str = 'display_name'

LEADER_BOARD_TITLE: str = 'Leaderboard rank: '
LIST_PLAYERS_TITLE: str = 'List of {} players'


class PlayerStatusEnum(Enum):
    UNPROCESSED = 'unprocessed'
    COMPETING = 'competing'
    NOT_COMPETING = 'not_competing'
    BANNED = 'banned'


ONLY_MODS: str = "Only Mods can use this command"
VALID_SUMMONER_NAME_REGEX: str = "\\w#\\w"


class ParticipationResponseEnum:
    SUCCESS = 'Success: Summoner account participation updated'
    UNPROCESSED = 'Failure: Summoner account is on waitlist'
    BANNED = 'Failure: Summoner account is banned'
    NO_PLAYER = 'Failure: Summoner account needs to be registered'
    NOT_CORRECT_DISCORD_ID = 'Failure: Summoner account was registered by a different discord user'


class CommandNameEnum(Enum):
    TEST = 'test'
    MOD_LEADERBOARD = 'mod_leaderboard'
    MOD_PROCESS_WAIT_LIST = 'mod_process_players_wait_list'
    MOD_PLAYERS_BY_STATUS = 'mod_get_players_by_status'
    REGISTER_FOR_RACE = 'join_ranked_race'
    PLAYER_PARTICIPATION = 'player_participation'
    HELP = 'help'


class CommandDescEnum:
    MOD_LEADERBOARD = 'Generate current leaderboard'
    MOD_PROCESS_WAIT_LIST = 'Process waitlist of players and let players into race'
    MOD_PLAYERS_BY_STATUS = 'Grabs list of players based on status'
    REGISTER_FOR_RACE = 'Register for ranked racing using your summoner name (EX: Player#123) and server (EX: NA)'
    PLAYER_PARTICIPATION = 'Allows Players to update their participation status in race'
    HELP = 'Shows all commands'


MOD_HELP: str = f"""
Mod Commands:
{"-" * 30}
{CommandNameEnum.MOD_LEADERBOARD}: {CommandDescEnum.MOD_LEADERBOARD}
{CommandNameEnum.MOD_PROCESS_WAIT_LIST}: {CommandDescEnum.MOD_PROCESS_WAIT_LIST}
{CommandNameEnum.MOD_PLAYERS_BY_STATUS}: {CommandDescEnum.MOD_PLAYERS_BY_STATUS}
{"-" * 30}
"""

PLAYER_HELP: str = f"""
->
\n
Player Commands
{"-" * 30}
{CommandNameEnum.REGISTER_FOR_RACE}: {CommandDescEnum.REGISTER_FOR_RACE}
{CommandNameEnum.PLAYER_PARTICIPATION}: {CommandDescEnum.PLAYER_PARTICIPATION}
{"-" * 30}

"""
