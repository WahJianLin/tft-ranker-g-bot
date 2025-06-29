import logging
from datetime import date

from src.actions.database import insert_player, get_players_by_status, insert_player_riot_data, \
    get_player_riot_data_by_ids, db_update_player_status, get_player_riot_data_by_id, get_player_by_summoner_name, \
    update_player_processed, get_missing_puuid, update_missing_puuid, db_update_player_display_name
from src.actions.riot_api import riot_get_ranks, riot_get_player_data_call, riot_get_missing_puuid
from src.actions.util import format_str_spacing_util
from src.resources.constants import REGION_MAP, SERVER_NAME_MAP, LEADER_BOARD_TITLE, ServerLocationEnum, \
    LIST_PLAYERS_TITLE, PlayerStatusEnum, ParticipationResponseEnum, PLAYER_HELP, MOD_HELP, DISCORD_TEXT_LIMIT
from src.resources.entity import Player, PlayerDataRes, LeaderboardEntry, PlayerRiotData


# Registering into waitlist
def register_player(
        summoner_name: str,
        location: ServerLocationEnum,
        display_name: str | None,
        discord_id: int,
        is_streamer: bool = False
) -> None:
    display_name_to_save: str = display_name if display_name is not None else summoner_name.split("#")[0]
    join_date: date = date.today()
    processed_date: date | None = None

    player: Player = Player(None, summoner_name.lower(), display_name_to_save, REGION_MAP[location],
                            SERVER_NAME_MAP[location],
                            join_date, processed_date, is_streamer, PlayerStatusEnum.UNPROCESSED.value, discord_id)
    insert_player(player)


# get list of unprocessed players
def get_player_by_status(status: PlayerStatusEnum) -> str:
    player_list: list[Player] = get_players_by_status(status)
    unprocessed_players_str: str = LIST_PLAYERS_TITLE.format(status.value) + '\n'
    unprocessed_players_str += '-' * 120 + '\n'
    space_in_between: int = 50
    for player in player_list:
        player_name_str = f"Player: {player.summoner_name}"
        player_name_str = format_str_spacing_util(player_name_str, space_in_between)
        display_name_str: str = f"Display Name: {player.display_name}"
        display_name_str = format_str_spacing_util(display_name_str, space_in_between)
        register_date_str = f"Register Date: {player.join_date}\n"

        player_detail_str: str = player_name_str + display_name_str + register_date_str
        unprocessed_players_str += player_detail_str
    unprocessed_players_str += '-' * 120 + '\n'

    return unprocessed_players_str


# processing waitlist
def process_waitlist() -> None:
    player_list: list[Player] = get_players_by_status()
    summoner_data_tpl: list[tuple[int, str]] = []  # player id and puuid
    player_ids: list[int] = []

    # gets list of unregistered players and player ids
    for player in player_list:

        player_data_res: PlayerDataRes = riot_get_player_data_call(player.summoner_name, player.region)

        if get_player_riot_data_by_id(player.id) is None:
            player_ids.append(player.id)
            summoner_data_tpl.append(
                (player.id, player_data_res.puuid))
        else:
            logging.info("Failed: Competitor already registered")

    # processes the players into competitors and updates relevant tables
    if summoner_data_tpl:
        insert_player_riot_data(summoner_data_tpl)

        player_riot_data_list: list[PlayerRiotData] = get_player_riot_data_by_ids(player_ids)

        processed_ids: list[int] = []

        for player_riot_data in player_riot_data_list:
            processed_ids.append(player_riot_data.player_id)

        if processed_ids:
            update_player_processed(processed_ids)
    else:
        logging.info("Failed: No Competitor to add")


def update_for_missing_puuid() -> None:
    missing_list: list[tuple[int, str, str]] = get_missing_puuid()
    if len(missing_list) > 0:
        puuid_list: list[tuple[int, str]] = riot_get_missing_puuid(missing_list)
        if len(puuid_list) > 0:
            update_missing_puuid(puuid_list)


# generating leaderboard
def sort_leaderboard(leaderboard_entries: list[LeaderboardEntry]) -> None:
    leaderboard_entries.sort(key=lambda entry: entry.tft_rank_value, reverse=True)


def gen_ranked_leaderboard_text(leaderboard_entries: list[LeaderboardEntry]) -> str:
    leaderboard_str: str = LEADER_BOARD_TITLE + '\n'

    formatted_final_leaderboard: list[str] = format_leader_board_entries(leaderboard_entries)
    for entry in formatted_final_leaderboard:
        leaderboard_str += entry + '\n'
    return leaderboard_str


def format_leader_board_entries(entries: list[LeaderboardEntry]) -> list[str]:
    rank_pos: int = 0
    last_rank_val: int = -1
    formatted_entries = []
    final_leaderboard: list[LeaderboardEntry] = []

    # clears out any potential duplicates
    for val in entries:
        if val not in final_leaderboard:
            final_leaderboard.append(val)
    # formats and populates entries
    for entry in final_leaderboard:
        if last_rank_val != entry.tft_rank_value:
            last_rank_val = entry.tft_rank_value
            rank_pos += 1
        player_name_rank: str = f'{rank_pos}) {entry.display_name}'
        player_name_rank = format_str_spacing_util(player_name_rank, 25)
        entry_detail: str = f'{player_name_rank}{entry.tft_rank_title}'
        formatted_entries.append(entry_detail)

    return formatted_entries


def get_leaderboard_result() -> str:
    leaderboard_entries: list[LeaderboardEntry] = riot_get_ranks()
    sort_leaderboard(leaderboard_entries)

    leaderboard_str: str = LEADER_BOARD_TITLE + '\n'

    formatted_final_leaderboard: list[str] = format_leader_board_entries(leaderboard_entries)
    for entry in formatted_final_leaderboard:
        leaderboard_str += entry + '\n'

    return leaderboard_str


def get_leaderboard_result_list() -> list[str]:
    leaderboard_entries: list[LeaderboardEntry] = riot_get_ranks()
    sort_leaderboard(leaderboard_entries)
    temp_str: str = LEADER_BOARD_TITLE + '\n'
    temp_str += ""
    leaderboard_str_list: list[str] = []

    formatted_leaderboard: list[str] = format_leader_board_entries(leaderboard_entries)
    for entry in range(len(formatted_leaderboard)):
        temp_str += formatted_leaderboard[entry] + '\n'
        if len(temp_str) > DISCORD_TEXT_LIMIT or entry >= len(formatted_leaderboard) - 1:
            leaderboard_str_list.append(temp_str)
            temp_str = '-' + '\n'
    return leaderboard_str_list


def update_participation(summoner_name: str, participation: bool, discord_id: int) -> str:
    player: Player | None = get_player_by_summoner_name(summoner_name)
    if player is not None:
        if player.player_status == PlayerStatusEnum.BANNED.value:
            return ParticipationResponseEnum.BANNED
        elif player.player_status == PlayerStatusEnum.UNPROCESSED.value:
            return ParticipationResponseEnum.UNPROCESSED
        elif player.discord_id != discord_id:
            return ParticipationResponseEnum.NOT_CORRECT_DISCORD_ID
        else:
            status: PlayerStatusEnum = PlayerStatusEnum.COMPETING if participation else PlayerStatusEnum.NOT_COMPETING
            db_update_player_status(player.id, status)
            return ParticipationResponseEnum.SUCCESS

    return ParticipationResponseEnum.NO_PLAYER


def generate_help_text(is_mod: bool) -> str:
    help_text: str = PLAYER_HELP
    if is_mod:
        help_text += MOD_HELP
    return help_text


def update_display_name(player_id: int, display_name: str):
    db_update_player_display_name(player_id, display_name)
