import logging
import os
from typing import Final

from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv

from src import slash_commands

load_dotenv()
DISCORD_TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client = commands.Bot(command_prefix="!", intents=intents)


# starting bot

@client.event
async def on_ready() -> None:
    print(f'{client.user} is running')
    try:
        synced = await client.tree.sync()
        print(f'Synced {len(synced)} commands(s)')
    except Exception as e:
        print(e)


# main
slash_commands.setup(client)


def main() -> None:
    client.run(token=DISCORD_TOKEN)


if __name__ == '__main__':
    main()
