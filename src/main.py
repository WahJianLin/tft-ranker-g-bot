from typing import Final
import os

from dotenv import load_dotenv
from discord import Intents, Message
from discord.ext import commands
from responses import get_response
from src import slash_commands

load_dotenv()
DISCORD_TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents: Intents = Intents.default()
intents.message_content = True # NOQA
client = commands.Bot(command_prefix="!", intents = intents)

# methods
async def send_message(message:Message, user_message: str) -> None:
    if not user_message:
        print('failed message')
        return

    try:
        response: str = get_response(user_message)
        await  message.channel.send(response)
    except Exception as e:
        print(e)

# starting bot

@client.event
async def on_ready()-> None:
    print(f'{client.user} is running')
    try:
        synced = await client.tree.sync()
        print(f'Synced {len(synced)} commands(s)')
    except Exception as e:
        print(e)

#main
slash_commands.setup(client)
def main() -> None:
    client.run(token=DISCORD_TOKEN)

if __name__ == '__main__':
    main()