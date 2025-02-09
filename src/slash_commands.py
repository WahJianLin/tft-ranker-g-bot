import asyncio
import re
import traceback

import discord
from discord.ext import commands

from src.actions.data_actions import register_player, get_leaderboard_result, process_waitlist
from src.actions.database import get_player_by_summoner_name
from src.actions.permission import is_mod
from src.actions.riot_api import get_player_data_call
from src.resources.constants import REGION_MAP, ServerLocationEnum

ONLY_MODS: str = "Only Mods can use this command"
VALID_SUMMONER_NAME_REGEX: str = "\\w#\\w"


async def test(interaction: discord.Interaction):
    await interaction.response.send_message("hello ajumma world")


async def get_leaderboard(interaction: discord.Interaction):
    if is_mod(interaction.user.roles):
        await interaction.response.defer()
        await asyncio.sleep(10)
        await interaction.followup.send(get_leaderboard_result())
    else:
        await interaction.response.send_message(ONLY_MODS, ephemeral=True)


async def join_ranked_race(interaction: discord.Interaction, summoner_name: str, location: ServerLocationEnum):
    try:
        if not re.search(VALID_SUMMONER_NAME_REGEX, summoner_name):
            await interaction.response.send_message(
                f"Failure: Invalid Summoner Name {summoner_name}. Summoner_name should match name#tag format",
                ephemeral=True)
        elif get_player_by_summoner_name(summoner_name) is not None:
            await interaction.response.send_message(
                f"Failure: {summoner_name} is already registered.",
                ephemeral=True)
        elif get_player_data_call(summoner_name, REGION_MAP[location]):
            register_player(summoner_name, location)
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


async def process_registered_players(interaction: discord.Interaction):
    if is_mod(interaction.user.roles):
        await interaction.response.defer()
        await asyncio.sleep(10)
        process_waitlist()
        await interaction.followup.send("Players have been processed into competitors.", ephemeral=True)
    else:
        await interaction.response.send_message(ONLY_MODS, ephemeral=True)




def setup(client: commands.Bot):
    client.tree.add_command(discord.app_commands.Command(name='test', callback=test, description='test command'))
    client.tree.add_command(discord.app_commands.Command(name='leaderboard', callback=get_leaderboard,
                                                         description='generate current leaderboard'))
    client.tree.add_command(discord.app_commands.Command(name='join_ranked_race', callback=join_ranked_race,
                                                         description='Joins Ranked TFT race. Requires Summoner name and region. EX: Player#NA1 NA'))
    client.tree.add_command(discord.app_commands.Command(name='process_players_wait_list', callback=process_registered_players,
                                                         description='Mod can allow players to join race'))
