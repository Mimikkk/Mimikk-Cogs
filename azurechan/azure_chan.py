from .ship_embed import ShipEmbed, cargo_query, ship_names
from .event_embed import EventEmbed
from .imports import *

class AzureCog(commands.Cog):
    """Azure Lane Cog"""

    def __init__(self):
        super().__init__()
        self.__update_ships()

    @staticmethod
    def __update_ships():
        """Updates ship data stored inside the Cog, Use seldom, it's Semi-Long"""
        cargo = cargo_query(tables="ships", fields="Name,Rarity", limit="500")

        for ship in cargo.json():
            if ship['Rarity'] != "Unreleased" and ship['Name'] not in ship_names:
                ship_names[unidecode(str(ship['Name'])).lower()] = str(ship['Name'])

    @commands.command(name="supported-ship-names")
    async def display_supported_ship_names(self, context: Context):

        pages = [*chat.pagify(chat.humanize_list(tuple(ship_names.values())), shorten_by=20)]
        len_ = len(pages)

        for (i, page) in enumerate(pages, 1):
            await context.send(f'**Page({i}/{len_})**\n{page}')

    @commands.command(name="shipgirl")
    async def chat_send_ship_embed(self, context: Context):
        """This sends menu with info about a shipgirl"""

        def extract_name(data: str) -> str:
            return unidecode(' '.join(re.findall(r'[^\s]+', data)[1:])).lower().strip()

        def find_similar_names(data: str) -> Tuple[str, ...]:
            return tuple(map(str, get_close_matches(word=data, possibilities=ship_names, n=3)))

        def format_similar_names(data: Tuple[str, ...]) -> str:
            return f"Did you mean {'any of these' if len(data) > 1 else 'this'} **{chat.humanize_list(data, style='or')}**?"

        if name := extract_name(context.message.content):
            if name not in ship_names and name != "random":
                await context.send("Name either mistyped or nonexistent.")
                if similar_names := find_similar_names(name):
                    await context.send(format_similar_names(similar_names))
            else:
                ship_embed: ShipEmbed = ShipEmbed(name if name != "random" else choice(tuple(ship_names.keys())))
                await menus.menu(context, pages=ship_embed.pages, controls=ship_embed.controls)
        else:
            await context.send("Name was not specified.")

    @commands.command(name="alevent")
    async def chat_send_event_embed(self, context: Context):
        """This sends info about recent events"""

        event_embed = EventEmbed()
        await menus.menu(context, pages=event_embed.pages, controls=event_embed.controls)
