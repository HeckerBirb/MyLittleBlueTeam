from discord.commands.context import ApplicationContext
from discord.ext import commands
from mysql.connector import connect

from src.cmds._proxy_helpers import Reply
from src.conf import GUILD_ID, MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASS
from src.mylittleblueteam import bot

"""
CREATE TABLE IF NOT EXISTS `trace` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` int(42) NOT NULL,
  `rarity` float(2,7) NOT NULL
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `inventory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(42) NOT NULL,
  `trace_id` int(11) NOT NULL
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


def name():
    return 'bust'


def description():
    return 'Bust the hackers by identifying the trace left behind.'


async def perform_action(ctx: ApplicationContext, reply):
    user_id = ctx.author.id
    trace_id = None  # TODO: get the item from the ongoing drop or fail if already finished
    trace_name = ''  # TODO: resolve this

    with connect(host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASS) as connection:
        with connection.cursor() as cursor:
            query_str = """INSERT INTO inventory (user_id, trace_id) VALUES (%s, %s)"""
            cursor.execute(query_str, (user_id, trace_id))
            connection.commit()

    await reply(ctx, f'{ctx.author} found 1 {trace_name}.', send_followup=False)


@bot.slash_command(guild_ids=[GUILD_ID], name=name(), description=description())
async def action_slash(ctx: ApplicationContext):
    await perform_action(ctx, Reply.slash)


@commands.command(name=name(), help=description())
async def action_prefix(ctx: ApplicationContext):
    await perform_action(ctx, Reply.prefix)


def setup(le_bot):
    le_bot.add_command(action_prefix)
