from .azure_chan import AzureCog
import redbot.core.bot as bots

def setup(bot: bots.RedBase):
    bot.add_cog(AzureCog())
