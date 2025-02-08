from datetime import date, datetime

from src.actions.database import insert_player, get_players, insert_competitors
from src.actions.riot_api import get_ranks, get_summoner_id_call, get_player_data_call
from src.resources.constants import ServerLocationEnum, REGION_MAP, SERVER_NAME_MAP, TFT_RANK_VALUE, LEADER_BOARD_TITLE, \
    DISPLAY_NAME, TFT_RANK_TITLE
from src.resources.entity import Player, PlayerDataRes

leaderboard = []


# Registering into waitlist
def register_player(summoner_name: str, location: ServerLocationEnum) -> None:
    display_name: str = summoner_name.split("#")[0]
    player: Player = Player(None, summoner_name, display_name, REGION_MAP[location], SERVER_NAME_MAP[location],
                            date.today(), False, None)
    insert_player(player)


# processing waitlist
def process_waitlist() -> None:
    players_tpl: list[tuple[Player, ...]] = get_players()
    for player_tpl in players_tpl:
        player: Player = Player.from_tuple(player_tpl)

        player_data_res: PlayerDataRes = get_player_data_call(player.summoner_name, player.region)
        summoner_id: str|None = get_summoner_id_call(player_data_res.puuid, player.riot_server)
        if summoner_id is not None:
            insert_competitors(player, summoner_id)


# generating leaderboard
def sort_leaderboard() -> None:
    leaderboard.sort(key=lambda x: x[TFT_RANK_VALUE], reverse=True)


def generate_leaderboard_display() -> str:
    now = datetime.now()
    dt_string = now.strftime('%B %d, %Y %I:%M:%S %p')
    leaderboard_str = LEADER_BOARD_TITLE + dt_string + '\n'
    leaderboard_str += '-' * 30 + '\n'
    rank_pos = 0
    last_rank_val = -1
    print("-" * 30)
    print(len(leaderboard))
    print(leaderboard)
    final_leaderboard = []

    for val in leaderboard:

        # Check if the value is not already in 'res'
        if val not in final_leaderboard:
            # If not present, append it to 'res'
            final_leaderboard.append(val)

    print(final_leaderboard)
    for entry in final_leaderboard:
        if last_rank_val != entry[TFT_RANK_VALUE]:
            rank_pos += 1
        entry_detail = f'{rank_pos}) {entry[DISPLAY_NAME]}    {entry[TFT_RANK_TITLE]}\n'
        leaderboard_str += entry_detail
    leaderboard_str += '-' * 30
    print(leaderboard_str)
    return leaderboard_str


def get_leaderboard_result() -> str:
    get_ranks(leaderboard)
    sort_leaderboard()
    return generate_leaderboard_display()
