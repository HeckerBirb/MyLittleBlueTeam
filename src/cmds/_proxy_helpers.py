import calendar
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Union, Optional, Tuple, Any

import discord
from discord import Forbidden, HTTPException, NotFound
from discord.commands.context import ApplicationContext
from mysql.connector import connect

from src.conf import RoleIDs, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS, HTB_URL, ChannelIDs
from src.lib.schedule import schedule
from src.log4soc import STDOUT_LOG


@dataclass
class PretendSnowflake:
    id: int


class Reply:
    @staticmethod
    def _log_call_and_msg(ctx, msg, **kwargs):
        STDOUT_LOG.debug(f'<Reply> cmd: "{ctx.command.name}", user: "{ctx.author.name}" ({ctx.author.id}), msg: "{msg}", kwargs: {kwargs}')

    """ Proxy for ctx.send and ctx.respond. Accepts same kwargs as the discord.InteractionResponse.send_message() does. """
    @staticmethod
    async def slash(ctx: ApplicationContext, msg=None, ephemeral=False, send_followup=False, **kwargs):
        if send_followup:
            await ctx.send_followup(content=msg, ephemeral=ephemeral, **kwargs)
        else:
            await ctx.respond(content=msg, ephemeral=ephemeral, **kwargs)
        Reply._log_call_and_msg(ctx, msg, **kwargs)

    @staticmethod
    async def prefix(ctx: ApplicationContext, msg=None, ephemeral=False, send_followup=False, **kwargs):
        # DO NOT remove named params ephemeral or send_followup. ApplicationContext.send(...) does not like these, so they must be "filtered away".
        await ctx.send(content=msg, **kwargs)
        Reply._log_call_and_msg(ctx, msg, **kwargs)


def get_user_id(user_id: Union[str, discord.Member]) -> Optional[int]:
    """ Get the user ID given a string of the ID, a string of the representation of the user mention, or a Discord Member object. """
    if user_id is None:
        return None
    if isinstance(user_id, discord.Member):
        user_id = user_id.id
    try:
        user_id = int(user_id.replace('<@', '').replace('!', '').replace('>', ''))
    except ValueError:
        return None

    return user_id


async def force_get_member(guild: discord.Guild, user_id: int) -> Optional[discord.Member]:
    """ Query Discord forcefully (no cache) for the user and return, if found. Otherwise return None. """
    try:
        STDOUT_LOG.debug(f'Forcefully obtaining member with ID {user_id} (no cache).')
        member = await guild.fetch_member(user_id)
        STDOUT_LOG.debug(f'Got member "{member.mention}"')
        return member
    except NotFound as ex:
        STDOUT_LOG.debug(f'Could not find member with id {user_id} on the server. Exception: {ex}')
        return None


def parse_duration_str(duration: str, baseline_ts: int = None) -> Optional[int]:
    """
    Converts an arbitrary measure of time, e.g. "3w" to a timestamp in seconds since 1970/01/01.
    Uses baseline_ts instead of the current time, if provided.
    """
    dur = re.compile(r'(-?(?:\d+\.?\d*|\d*\.?\d+)(?:e[-+]?\d+)?)\s*([a-z]*)', re.IGNORECASE)
    units = {'s': 1}
    units['m'] = units['min'] = units['mins'] = units['s'] * 60
    units['h'] = units['hr'] = units['hour'] = units['hours'] = units['m'] * 60
    units['d'] = units['day'] = units['days'] = units['h'] * 24
    units['wk'] = units['w'] = units['week'] = units['weeks'] = units['d'] * 7
    units['month'] = units['months'] = units['mo'] = units['d'] * 30
    units['y'] = units['yr'] = units['d'] * 365
    sum_seconds = 0

    while duration:
        m = dur.match(duration)
        if not m:
            return None
        duration = duration[m.end():]
        sum_seconds += int(m.groups()[0]) * units.get(m.groups()[1], 1)

    if baseline_ts is None:
        epoch_time = calendar.timegm(time.gmtime())
    else:
        epoch_time = baseline_ts
    return epoch_time + sum_seconds


def member_is_staff(member: discord.Member) -> bool:
    """ Checks if a member has any of the Administrator or Moderator roles defined in the RoleIDs class. """
    for role in member.roles:
        if role.id in RoleIDs.ALL_ADMINS + RoleIDs.ALL_MODS:
            return True

    return False


def remove_record(delete_query: str, id_to_remove: Tuple[Any, ...]) -> None:
    """ Delete a record from the database, given a one tuple of values for the delete query to use. """
    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            cursor.execute(delete_query, id_to_remove)
            connection.commit()
