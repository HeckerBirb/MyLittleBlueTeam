import os
from os.path import dirname, abspath
from pathlib import Path

from discord.commands import commands

from src.log4soc import STDOUT_LOG


def _get_int_env(env_var: str, default: str = None) -> int:
    try:
        STDOUT_LOG.debug(f'Loading {env_var} (default={default}).')
        return int(os.getenv(env_var, default))
    except KeyError:
        STDOUT_LOG.critical(f'Environment variable {env_var} cannot be parsed as an int!')
        exit(1)


GUILD_ID = _get_int_env('GUILD_ID')
ROOT_DIR = Path(dirname(dirname(abspath(__file__))))

MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = _get_int_env('MYSQL_PORT', '3306')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'mylittleblueteam')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASS = os.getenv('MYSQL_PASSWORD', None)
if MYSQL_PASS is None:
    MYSQL_PASS = os.getenv('MYSQL_ROOT_PASSWORD', 'mlbt')


class ChannelIDs:
    BOT_COMMANDS = _get_int_env('BOT_COMMANDS_CHAN')


def _allow(role_id):
    return commands.Permission(id=role_id, type=1, permission=True)


class RoleIDs:
    # Individual roles
    BOT_ADMIN = _get_int_env('BOT_ADMIN_ROLE')

    # Role collections
    ALL_ADMINS = [BOT_ADMIN]


class SlashPerms:
    """ IDs for the specific roles. Note that due to the way slash commands handle permissions, these are SINGULAR. """
    ADMIN = _allow(RoleIDs.BOT_ADMIN)


class PrefixPerms:
    """ IDs for the specific roles. Note that due to the way prefix commands handle permissions, these are PLURAL. """
    ALL_ADMINS = RoleIDs.ALL_ADMINS
