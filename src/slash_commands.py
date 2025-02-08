import asyncio
import re
import traceback

import discord
from discord.ext import commands

from src.actions.database import get_unprocessed_player_by_summoner_name
from src.actions.riot_api import get_leaderboard_result, register_tft_race, SERVER_LOCATION, \
    get_player_data_call
from src.actions.permission import is_mod

ONLY_MODS = "Only Mods can use this command"
VALID_SUMMONER_NAME_REGEX = "\\w#\\w"


async def test(interaction: discord.Interaction):
    await interaction.response.send_message("hello ajumma world")


async def get_leaderboard(interaction: discord.Interaction):
    if is_mod(interaction.user.roles):
        await interaction.response.defer()
        await asyncio.sleep(30)
        await interaction.followup.send(get_leaderboard_result())
    else:
        await interaction.response.send_message(ONLY_MODS, ephemeral=True)


async def join_ranked_race(interaction: discord.Interaction, summoner_name: str, location: SERVER_LOCATION):
    try:
        if not re.search(VALID_SUMMONER_NAME_REGEX, summoner_name):
            await interaction.response.send_message(
                f"Failure: Invalid Summoner Name {summoner_name}. Summoner_name should match name#tag format",
                ephemeral=True)
        elif get_unprocessed_player_by_summoner_name(summoner_name) is not None:
            await interaction.response.send_message(
                f"Failure: {summoner_name} is already registered.",
                ephemeral=True)
        elif get_player_data_call(summoner_name, location):
            register_tft_race(summoner_name, location)
            await interaction.response.send_message(
                f"Success: {summoner_name} Registered. Please wait until this Saturday to be officially added into the race",
                ephemeral=True)
        else:
            await interaction.response.send_message(
                f"Failure: Summoner Name {summoner_name} not found on riot database.",
                ephemeral=True)
    except Exception:
        traceback.print_exc()
        await interaction.response.send_message(f"Failure: Unexpected Error",
                                                ephemeral=True)


def setup(client: commands.Bot):
    client.tree.add_command(discord.app_commands.Command(name='test', callback=test, description='test command'))
    client.tree.add_command(discord.app_commands.Command(name='leaderboard', callback=get_leaderboard,
                                                         description='generate current leaderboard'))
    client.tree.add_command(discord.app_commands.Command(name='join_ranked_race', callback=join_ranked_race,
                                                         description='Joins Ranked TFT race. Requires Summoner name and region. EX: Player#NA1 NA'))
