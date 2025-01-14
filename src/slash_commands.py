import discord
from discord.ext import commands


async def test(interaction: discord.Interaction):
    await interaction.response.send_message('test2')

def setup(client: commands.Bot):
    client.tree.add_command(discord.app_commands.Command(name='test', callback=test, description='test command'))
