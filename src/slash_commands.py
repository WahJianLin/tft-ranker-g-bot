import asyncio

import discord
from discord.ext import commands
from src.actions.generate_leaderboard import get_leaderboard_result
from src.actions.permission import is_mod

ONLY_MODS = "Only Mods can use this command"

async def test(interaction: discord.Interaction):
    if is_mod(interaction.user.roles):
        await interaction.response.send_message("hello ajumma world")
    else:
        await interaction.response.send_message("hello not ajumma world")


async def get_leaderboard(interaction: discord.Interaction):
    if is_mod(interaction.user.roles):
        await interaction.response.defer()
        await asyncio.sleep(30)
        await interaction.followup.send(get_leaderboard_result())
    else:
        await interaction.response.send_message(ONLY_MODS, ephemeral=True)


def setup(client: commands.Bot):
    client.tree.add_command(discord.app_commands.Command(name='test', callback=test, description='test command'))
    client.tree.add_command(discord.app_commands.Command(name='leaderboard', callback=get_leaderboard,
                                                         description='generate current leaderboard'))
