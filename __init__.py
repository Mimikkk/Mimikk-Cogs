import redbot.core.bot as bots
from .azure_chan import AzureCog

def setup(bot: bots.RedBase):
    bot.add_cog(AzureCog())
