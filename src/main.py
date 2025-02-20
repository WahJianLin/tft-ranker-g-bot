import asyncio
import logging
import os
from typing import Final

from discord import Intents
from discord.ext import commands, tasks
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

@tasks.loop(seconds=10)
async def called_once_a_day():
    message_channel = client.get_channel('thing')
    print(f"Got channel {message_channel}")
    await message_channel.send("Your message")

@called_once_a_day.before_loop
async def before():
    await client.wait_until_ready()
    print("Finished waiting")

@client.event
async def on_ready() -> None:
    print(f'{client.user} is running')
    try:
        synced = await client.tree.sync()
        called_once_a_day.start()
        print(f'Synced {len(synced)} commands(s)')
    except Exception as e:
        print(e)


# main
slash_commands.setup(client)


# def main() -> None:
#     client.run(token=DISCORD_TOKEN)

def main():
    asyncio.run(start_bot())  # Explicitly create an event loop

async def start_bot():
    async with client:
        await client.start(DISCORD_TOKEN)

if __name__ == '__main__':
    main()
