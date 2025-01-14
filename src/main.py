from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents: Intents = Intents.default()
intents.message_content = True # NOQA
client: Client = Client(intents=intents)

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

#on message event
@client.event
async def on_message(message:Message) -> None:
    if(message.author == client.user):
        return

    user_name: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {user_name}: {user_message}')
    await send_message(message, user_message)

#main
def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()