from datetime import date, datetime

from src.actions.database import insert_unprocessed_players
from src.resources.constants import ServerLocationEnum, REGION_MAP, SERVER_NAME_MAP, TFT_RANK_VALUE, LEADER_BOARD_TITLE, \
    DISPLAY_NAME, TFT_RANK_TITLE
from src.resources.entity import Player

leaderboard = []
total_api_calls = 0


def register_tft_race(summoner_name: str, location: ServerLocationEnum) -> None:
    display_name: str = summoner_name.split("#")[0]
    player: Player = Player(None, summoner_name, display_name, REGION_MAP[location], SERVER_NAME_MAP[location],
                            date.today(), False, None)
    insert_unprocessed_players(player)


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
    get_ranks()
    sort_leaderboard()
    return generate_leaderboard_display()
