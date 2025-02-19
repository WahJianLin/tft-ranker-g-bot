import asyncio
import logging
import re

import discord
from discord.ext import commands

from src.actions.data_actions import register_player, get_leaderboard_result, process_waitlist
from src.actions.database import get_player_by_summoner_name
from src.actions.permission import is_mod
from src.actions.riot_api import get_player_data_call
from src.resources.constants import REGION_MAP, SlashCommands, ONLY_MODS, VALID_SUMMONER_NAME_REGEX
from src.resources.logging_constants import SLASH_COMMANDS, COMMAND_SUCCESS, COMMAND_FAIL, COMMAND_ERROR_UNEXPECTED, \
    COMMAND_ERROR_SUMMONER_NAME, COMMAND_ERROR_EXISTING_SUMMONER, COMMAND_SUCCESS_SUMMONER_REGISTERED, \
    COMMAND_ERROR_SUMMONER_NOT_FOUND, COMMAND_SUCCESS_PROCESS


async def test(interaction: discord.Interaction):
    logging.info(SLASH_COMMANDS.format(SlashCommands.TEST.value))
    await interaction.response.send_message("hello ajumma world")


async def get_leaderboard(interaction: discord.Interaction):
    try:
        logging.info(SLASH_COMMANDS.format(SlashCommands.LEADERBOARD.value))
        if is_mod(interaction.user.roles):
            await interaction.response.defer()
            await asyncio.sleep(10)
            await interaction.followup.send(get_leaderboard_result())
        else:
            await interaction.response.send_message(ONLY_MODS, ephemeral=True)
        logging.info(SLASH_COMMANDS.format(COMMAND_SUCCESS))
    except Exception as e:
        logging.info(SLASH_COMMANDS.format(COMMAND_FAIL))
        logging.exception(e)
        await interaction.response.send_message(COMMAND_ERROR_UNEXPECTED,
                                                ephemeral=True)


async def join_ranked_race(interaction: discord.Interaction, summoner_name: str, location: SlashCommands):
    try:
        logging.info(SLASH_COMMANDS.format(SlashCommands.JOIN_RANKED_RACE.value))
        if not re.search(VALID_SUMMONER_NAME_REGEX, summoner_name):
            await interaction.response.send_message(
                COMMAND_ERROR_SUMMONER_NAME.format(summoner_name),
                ephemeral=True)
        elif get_player_by_summoner_name(summoner_name) is not None:
            await interaction.response.send_message(
                COMMAND_ERROR_EXISTING_SUMMONER.format(summoner_name),
                ephemeral=True)
        elif get_player_data_call(summoner_name, REGION_MAP[location]):
            # registers player
            register_player(summoner_name, location)
            logging.info(SLASH_COMMANDS.format(COMMAND_SUCCESS))
            await interaction.response.send_message(
                COMMAND_SUCCESS_SUMMONER_REGISTERED.format(summoner_name),
                ephemeral=True)
            logging.info(SLASH_COMMANDS.format(SlashCommands.JOIN_RANKED_RACE.value))
        else:
            await interaction.response.send_message(
                COMMAND_ERROR_SUMMONER_NOT_FOUND.format(summoner_name),
                ephemeral=True)
    except Exception as e:
        logging.info(SLASH_COMMANDS.format(COMMAND_FAIL))
        logging.exception(e)
        await interaction.response.send_message(COMMAND_ERROR_UNEXPECTED,
                                                ephemeral=True)


async def process_registered_players(interaction: discord.Interaction):
    try:
        logging.info(SLASH_COMMANDS.format(SlashCommands.JOIN_RANKED_RACE.value))
        if is_mod(interaction.user.roles):
            await interaction.response.defer()
            await asyncio.sleep(10)
            process_waitlist()
            await interaction.followup.send(COMMAND_SUCCESS_PROCESS, ephemeral=True)
            logging.info(SLASH_COMMANDS.format(COMMAND_SUCCESS))
        else:
            await interaction.response.send_message(ONLY_MODS, ephemeral=True)
    except Exception as e:
        logging.info(SLASH_COMMANDS.format(COMMAND_FAIL))
        logging.exception(e)
        await interaction.response.send_message(COMMAND_ERROR_UNEXPECTED,
                                                ephemeral=True)


def setup(client: commands.Bot):
    client.tree.add_command(discord.app_commands.Command(name='test', callback=test, description='test command'))
    client.tree.add_command(discord.app_commands.Command(name='leaderboard', callback=get_leaderboard,
                                                         description='generate current leaderboard'))
    client.tree.add_command(discord.app_commands.Command(name='join_ranked_race', callback=join_ranked_race,
                                                         description='Joins Ranked TFT race. Requires Summoner name and region. EX: Player#NA1 NA'))
    client.tree.add_command(
        discord.app_commands.Command(name='process_players_wait_list', callback=process_registered_players,
                                     description='Mod can allow players to join race'))
