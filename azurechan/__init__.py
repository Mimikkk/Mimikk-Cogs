from .azure_chan import AzureCog
import redbot.core.bot as bots

def setup(bot: bots.Red):
    bot.add_cog(AzureCog())
