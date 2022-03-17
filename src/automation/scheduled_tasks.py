from datetime import datetime
from discord.ext import tasks
from src.lib.schedule import schedule


@tasks.loop(hours=3)
def leak_trace():
    async def leak():
        """ "Leaks" one trace in a random channel. """
        # FIXME: refactor this someplace nice
        pass

    now = datetime.now()
    schedule(leak(), run_at=now)

    return []


def setup(_):
    leak_trace.start()
