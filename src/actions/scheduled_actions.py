import logging
import os
from datetime import datetime
from typing import Final

from discord.ext import tasks
from dotenv import load_dotenv

from src.actions.data_actions import get_leaderboard_result_list

load_dotenv()
LEADERBOARD_CHANNEL: Final[int] = int(os.getenv('LEADERBOARD_CHANNEL'))
RUN_TIMES_STR: list[str] = os.getenv('SCHEDULE_LEADERBOARD_TIMES').split(",")
RUN_TIMES: list[int] = list(map(int, RUN_TIMES_STR))


@tasks.loop(minutes=60)
async def schedule_leaderboard_caller(client):
    cur_hour: int = datetime.now().hour
    message_channel = client.get_channel(LEADERBOARD_CHANNEL)

    if message_channel:
        logging.info(f"schedule_leaderboard_caller triggered at {cur_hour} utc hour")
        if cur_hour in RUN_TIMES:
            logging.info(f"schedule_leaderboard_caller starting")
            try:
                formatted_list: list[str] = get_leaderboard_result_list()
                for entry in formatted_list:
                    await message_channel.send(entry)
            except Exception as e:
                logging.error(f"schedule_leaderboard_caller Unexpected Error Failed")
                logging.exception(e)
    else:
        logging.error("schedule_leaderboard_caller Channel Not found")
