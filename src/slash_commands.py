import asyncio

import discord
from discord.ext import commands
from src.actions.generate_leaderboard import get_leaderboard_result


async def test(interaction: discord.Interaction):
    await interaction.response.send_message("hello ajumma world")


async def get_leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()
    await asyncio.sleep(30)
    await interaction.followup.send(get_leaderboard_result())


def setup(client: commands.Bot):
    client.tree.add_command(discord.app_commands.Command(name='test', callback=test, description='test command'))
    client.tree.add_command(discord.app_commands.Command(name='leaderboard', callback=get_leaderboard,
                                                         description='generate current leaderboard'))
