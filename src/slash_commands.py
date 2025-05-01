import asyncio
import logging
import re

import discord
from discord.ext import commands
from profanity_check import predict, predict_prob

from src.actions.data_actions import get_leaderboard_result, process_waitlist, get_player_by_status, register_player, \
    update_participation, generate_help_text, update_display_name
from src.actions.database import get_player_by_summoner_name
from src.actions.permission import is_mod
from src.actions.riot_api import get_player_data_call
from src.actions.validators import validate_summoner_name_and_display_name, validate_discord_id
from src.resources.constants import REGION_MAP, SlashCommands, ONLY_MODS, VALID_SUMMONER_NAME_REGEX, ServerLocationEnum, \
    PlayerStatusEnum, CommandNameEnum, CommandDescriptionEnum
from src.resources.entity import Player
from src.resources.logging_constants import SLASH_COMMANDS, COMMAND_SUCCESS, COMMAND_FAIL, COMMAND_ERROR_UNEXPECTED, \
    COMMAND_ERROR_SUMMONER_NAME, ERROR_EXISTING_SUMMONER, COMMAND_SUCCESS_SUMMONER_REGISTERED, \
    COMMAND_ERROR_SUMMONER_NOT_FOUND, COMMAND_SUCCESS_PROCESS, PERMISSION_IS_NOT_MOD, COMMAND_ERROR_DISPLAY_NAME_LENGTH, \
    COMMAND_SUCCESS_DISPLAY_NAME, COMMAND_ERROR_DISPLAY_NAME_PROFANITY


async def test_command(interaction: discord.Interaction):
    logging.info(SLASH_COMMANDS.format(SlashCommands.TEST.value))
    await interaction.response.send_message("hello ajumma world")

async def mod_get_leaderboard_command(interaction: discord.Interaction):
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


async def join_ranked_race_command(interaction: discord.Interaction, summoner_name: str, server: ServerLocationEnum,
                                   display_name: str | None, is_streamer: bool = False):
    try:
        logging.info(SLASH_COMMANDS.format(SlashCommands.JOIN_RANKED_RACE.value))
        logging.info(
            f"With Data -> summoner_name: {summoner_name}, server: {server}, display_name: {display_name}, is_streamer: {is_streamer}")

        # todo update to use proper validator
        if not re.search(VALID_SUMMONER_NAME_REGEX, summoner_name):
            await interaction.response.send_message(
                COMMAND_ERROR_SUMMONER_NAME.format(summoner_name),
                ephemeral=True)
        elif display_name is not None and (len(display_name) < 3 or len(display_name) > 16):
            await interaction.response.send_message(
                COMMAND_ERROR_DISPLAY_NAME_LENGTH,
                ephemeral=True)
        elif get_player_by_summoner_name(summoner_name) is not None:
            await interaction.response.send_message(
                ERROR_EXISTING_SUMMONER.format(summoner_name),
                ephemeral=True)
        elif predict_prob([display_name])[0]> .6:
            await interaction.response.send_message(
                COMMAND_ERROR_DISPLAY_NAME_PROFANITY,
                ephemeral=True)
        elif get_player_data_call(summoner_name, REGION_MAP[server]):
            await interaction.response.defer()
            await asyncio.sleep(5)
            # registers player
            register_player(summoner_name, server, display_name, interaction.user.id, is_streamer)

            logging.info(SLASH_COMMANDS.format(COMMAND_SUCCESS))
            await interaction.followup.send(
                COMMAND_SUCCESS_SUMMONER_REGISTERED,
                ephemeral=True)
            logging.info(SLASH_COMMANDS.format(SlashCommands.JOIN_RANKED_RACE.value))
        else:
            await interaction.response.send_message(
                COMMAND_ERROR_SUMMONER_NOT_FOUND.format(summoner_name),
                ephemeral=True)
    except Exception as e:
        logging.info(SLASH_COMMANDS.format(COMMAND_FAIL))
        logging.exception(e)
        await interaction.response.send_message(
            COMMAND_ERROR_UNEXPECTED,
            ephemeral=True)


async def mod_process_registered_players_command(interaction: discord.Interaction):
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


async def mod_get_players_by_status_command(interaction: discord.Interaction, status: PlayerStatusEnum):
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


# used word participation instead of competition since it sounds a bit better
async def update_participation_command(interaction: discord.Interaction, summoner_name: str, participation: bool):
    try:
        logging.info(SLASH_COMMANDS.format(SlashCommands.UPDATE_PARTICIPATION.value))

        await interaction.response.send_message(update_participation(summoner_name.lower(), participation, interaction.user.id),
                                                ephemeral=True)
    except Exception as e:
        logging.info(SLASH_COMMANDS.format(COMMAND_FAIL))
        logging.exception(e)
        await interaction.response.send_message(COMMAND_ERROR_UNEXPECTED,
                                                ephemeral=True)


async def help_command(interaction: discord.Interaction):
    logging.info(SLASH_COMMANDS.format(SlashCommands.HELP.value))
    await interaction.response.send_message(generate_help_text(is_mod(interaction.user.roles)))



# here
async def update_display_name_command(interaction: discord.Interaction, summoner_name: str, display_name: str):
    try:
        logging.info(SLASH_COMMANDS.format(SlashCommands.UPDATE_DISPLAY_NAME.value))
        validate_summoner_name_and_display_name(summoner_name, display_name)
        player: Player | None = get_player_by_summoner_name(summoner_name)
        validate_discord_id(player, interaction.user.id)
        update_display_name(player.id, display_name)

        await interaction.response.defer()
        await asyncio.sleep(5)

        await interaction.followup.send(COMMAND_SUCCESS_DISPLAY_NAME, ephemeral=True)
        logging.info(SLASH_COMMANDS.format(COMMAND_SUCCESS))
    except ValueError as e:
        await interaction.response.send_message(e,ephemeral=True)
    except Exception as e:
        logging.info(SLASH_COMMANDS.format(COMMAND_FAIL))
        logging.exception(e)
        await interaction.response.send_message(COMMAND_ERROR_UNEXPECTED,
                                                ephemeral=True)

    pass



# TODO look to use annotation instead of set up below. If it is worth the time.
def setup(client: commands.Bot):
    client.tree.add_command(discord.app_commands.Command(
        name='test',
        callback=test_command,
        description='test command')
    )
    client.tree.add_command(discord.app_commands.Command(
        name=CommandNameEnum.MOD_LEADERBOARD,
        callback=mod_get_leaderboard_command,
        description=CommandDescriptionEnum.MOD_LEADERBOARD)
    )
    client.tree.add_command(discord.app_commands.Command(
        name=CommandNameEnum.REGISTER_FOR_RACE,
        callback=join_ranked_race_command,
        description=CommandDescriptionEnum.REGISTER_FOR_RACE)
    )
    client.tree.add_command(discord.app_commands.Command(
        name=CommandNameEnum.MOD_PROCESS_WAIT_LIST,
        callback=mod_process_registered_players_command,
        description=CommandDescriptionEnum.MOD_PROCESS_WAIT_LIST)
    )
    client.tree.add_command(discord.app_commands.Command(
        name=CommandNameEnum.MOD_PLAYERS_BY_STATUS,
        callback=mod_get_players_by_status_command,
        description=CommandDescriptionEnum.MOD_PLAYERS_BY_STATUS)
    )
    client.tree.add_command(discord.app_commands.Command(
        name=CommandNameEnum.PLAYER_PARTICIPATION,
        callback=update_participation_command,
        description=CommandDescriptionEnum.PLAYER_PARTICIPATION)
    )
    client.tree.add_command(discord.app_commands.Command(
        name=CommandNameEnum.HELP,
        callback=help_command,
        description=CommandDescriptionEnum.HELP)
    )
    client.tree.add_command(discord.app_commands.Command(
        name=CommandNameEnum.UPDATE_DISPLAY_NAME,
        callback=update_display_name_command,
        description=CommandDescriptionEnum.UPDATE_DISPLAY_NAME)
    )
