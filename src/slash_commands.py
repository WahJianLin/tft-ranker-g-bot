import asyncio
import logging
import re

import discord
from discord.ext import commands

from src.actions.data_actions import get_leaderboard_result, process_waitlist, get_player_by_status, register_player, \
    update_participation
from src.actions.database import get_player_by_summoner_name
from src.actions.permission import is_mod
from src.actions.riot_api import get_player_data_call
from src.resources.constants import REGION_MAP, SlashCommands, ONLY_MODS, VALID_SUMMONER_NAME_REGEX, ServerLocationEnum, \
    PlayerStatusEnum
from src.resources.logging_constants import SLASH_COMMANDS, COMMAND_SUCCESS, COMMAND_FAIL, COMMAND_ERROR_UNEXPECTED, \
    COMMAND_ERROR_SUMMONER_NAME, ERROR_EXISTING_SUMMONER, COMMAND_SUCCESS_SUMMONER_REGISTERED, \
    COMMAND_ERROR_SUMMONER_NOT_FOUND, COMMAND_SUCCESS_PROCESS, PERMISSION_IS_NOT_MOD, COMMAND_ERROR_DISPLAY_NAME_LENGTH


async def test(interaction: discord.Interaction):
    logging.info(SLASH_COMMANDS.format(SlashCommands.TEST.value))
    await interaction.response.send_message("hello ajumma world")


async def get_leaderboard_command(interaction: discord.Interaction):
    try:
        logging.info(SLASH_COMMANDS.format(SlashCommands.LEADERBOARD.value))
        if is_mod(interaction.user.roles):
            await interaction.response.defer()
            await asyncio.sleep(10)
            await interaction.followup.send(get_leaderboard_result())
            logging.info(SLASH_COMMANDS.format(COMMAND_SUCCESS))
        else:
            await interaction.response.send_message(ONLY_MODS, ephemeral=True)
            logging.info(PERMISSION_IS_NOT_MOD)
    except Exception as e:
        logging.info(SLASH_COMMANDS.format(COMMAND_FAIL))
        logging.exception(e)
        await interaction.response.send_message(COMMAND_ERROR_UNEXPECTED,
                                                ephemeral=True)


async def join_ranked_race_command(interaction: discord.Interaction, summoner_name: str, location: ServerLocationEnum,
                                   display_name: str | None, is_streamer: bool = False):
    try:
        logging.info(SLASH_COMMANDS.format(SlashCommands.JOIN_RANKED_RACE.value))
        logging.info(
            f"With Data -> summoner_name: {summoner_name}, location: {location}, display_name: {display_name}, is_streamer: {is_streamer}")

        await interaction.response.defer()
        await asyncio.sleep(10)

        if not re.search(VALID_SUMMONER_NAME_REGEX, summoner_name):
            await interaction.followup.send(
                COMMAND_ERROR_SUMMONER_NAME.format(summoner_name),
                ephemeral=True)
        elif display_name is not None and (len(display_name) < 3 or len(display_name) > 16):
            await interaction.followup.send(
                COMMAND_ERROR_DISPLAY_NAME_LENGTH,
                ephemeral=True)
        elif get_player_by_summoner_name(summoner_name) is not None:
            await interaction.followup.send(
                ERROR_EXISTING_SUMMONER.format(summoner_name),
                ephemeral=True)
        # To Do filter out malicious display names
        elif get_player_data_call(summoner_name, REGION_MAP[location]):
            # registers player
            register_player(summoner_name, location, display_name, interaction.user.id, is_streamer)

            logging.info(SLASH_COMMANDS.format(COMMAND_SUCCESS))
            await interaction.followup.send(
                COMMAND_SUCCESS_SUMMONER_REGISTERED.format(summoner_name),
                ephemeral=True)
            logging.info(SLASH_COMMANDS.format(SlashCommands.JOIN_RANKED_RACE.value))
        else:
            await interaction.followup.send(
                COMMAND_ERROR_SUMMONER_NOT_FOUND.format(summoner_name),
                ephemeral=True)
    except Exception as e:
        logging.info(SLASH_COMMANDS.format(COMMAND_FAIL))
        logging.exception(e)
        await interaction.followup.send(
            COMMAND_ERROR_UNEXPECTED,
            ephemeral=True)


async def process_registered_players_command(interaction: discord.Interaction):
    try:
        logging.info(SLASH_COMMANDS.format(SlashCommands.PROCESS_PLAYERS.value))
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


async def get_players_by_status_command(interaction: discord.Interaction, status: PlayerStatusEnum):
    try:
        logging.info(SLASH_COMMANDS.format(SlashCommands.GET_PLAYER_STATUS.value))
        if is_mod(interaction.user.roles):
            await interaction.response.defer()
            await asyncio.sleep(10)

            await interaction.followup.send(get_player_by_status(status), ephemeral=True)
            logging.info(SLASH_COMMANDS.format(COMMAND_SUCCESS))
        else:
            await interaction.response.send_message(ONLY_MODS, ephemeral=True)
    except Exception as e:
        logging.info(SLASH_COMMANDS.format(COMMAND_FAIL))
        logging.exception(e)
        await interaction.response.send_message(COMMAND_ERROR_UNEXPECTED,
                                                ephemeral=True)


#used word participation instead of competition since it sounds a bit better
async def update_participation_command(interaction: discord.Interaction, summoner_name: str, participation: bool):
    try:
        logging.info(SLASH_COMMANDS.format(SlashCommands.UPDATE_PARTICIPATION.value))
        await interaction.response.defer()
        await asyncio.sleep(10)

        await interaction.followup.send(update_participation(summoner_name, participation), ephemeral=True)
        logging.info(SLASH_COMMANDS.format(COMMAND_SUCCESS))
    except Exception as e:
        logging.info(SLASH_COMMANDS.format(COMMAND_FAIL))
        logging.exception(e)
        await interaction.response.send_message(COMMAND_ERROR_UNEXPECTED,
                                                ephemeral=True)


def setup(client: commands.Bot):
    client.tree.add_command(discord.app_commands.Command(name='test', callback=test, description='test command'))
    client.tree.add_command(discord.app_commands.Command(name='leaderboard', callback=get_leaderboard_command,
                                                         description='generate current leaderboard'))
    client.tree.add_command(discord.app_commands.Command(name='join_ranked_race', callback=join_ranked_race_command,
                                                         description='Joins Ranked TFT race. Requires Summoner name and region. EX: Player#NA1 NA'))
    client.tree.add_command(
        discord.app_commands.Command(name='process_players_wait_list', callback=process_registered_players_command,
                                     description='Mod can allow players to join race'))
    client.tree.add_command(
        discord.app_commands.Command(name='get_unprocessed_players', callback=get_players_by_status_command,
                                     description='Mod can see players to register'))
    client.tree.add_command(
        discord.app_commands.Command(name='player_participation', callback=update_participation_command,
                                     description='Player can determine participation'))
