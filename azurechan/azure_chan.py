from .ship_embed import ShipEmbed, cargo_query, ship_names
from .event_embed import EventEmbed
from .items_embed import ItemEmbed, item_names
from .imports import *


class AzureCog(commands.Cog):
    """Azure Lane Cog"""

    def __init__(self):
        super().__init__()
        self.__update_ships()
        self.__update_items()

    @staticmethod
    def __update_ships():
        """Updates ship data stored inside the Cog"""
        cargo = cargo_query(tables="ships", fields="Name,Rarity", limit="500")

        for ship in cargo.json():
            if ship['Rarity'] != "Unreleased" and ship['Name'] not in ship_names:
                ship_names[unidecode(str(ship['Name'])).lower()] = str(ship['Name'])

    @staticmethod
    def __update_items():
        """Updates item data stored inside the Cog"""
        cargo_dict: Dict = cargo_query(tables="equipment", fields="Name", limit="500").json()
        cargo_dict += cargo_query(tables="equipment", fields="Name", offset="450", limit="500").json()

        for item in cargo_dict:
            item_names[unidecode(str(item['Name'])).lower()] = str(item['Name'])

    @commands.command(name="update-supported-item-names")
    async def update_items(self):
        """Updates item data stored inside the Cog, Use seldom, it's Semi-Long"""
        self.__update_items()

    @commands.command(name="update-supported-ship-names")
    async def update_ships(self):
        """Updates ship data stored inside the Cog, Use seldom, it's Semi-Long"""
        self.__update_ships()

    @commands.command(name="supported-ship-names")
    async def display_supported_ship_names(self, context: Context):
        """Displays supported ship names"""
        pages = [*chat.pagify(chat.humanize_list(tuple(ship_names.values())), shorten_by=20)]
        len_ = len(pages)

        for (i, page) in enumerate(pages, 1):
            await context.send(f'**Page({i}/{len_})**\n{page}')

    @commands.command(name="supported-item-names")
    async def display_supported_item_names(self, context: Context):
        """Displays supported item names"""
        pages = [*chat.pagify(chat.humanize_list(tuple(item_names.values())), shorten_by=20)]
        len_ = len(pages)

        for (i, page) in enumerate(pages, 1):
            await context.send(f'**Page({i}/{len_})**\n{page}')

    @commands.command(name="shipitem")
    async def chat_send_item_embed(self, context: Context):
        """This sends menu with info about a azur lane item"""
        if isinstance(embed_data := self.chat_get_embed(context, 'item'), str):
            await context.send(embed_data)
        else:
            await menus.menu(context, pages=embed_data.pages, controls=embed_data.controls)

    @commands.command(name="shipgirl")
    async def chat_send_ship_embed(self, context: Context):
        """This sends menu with info about a azur lane shipgirl"""
        if isinstance(embed_data := self.chat_get_embed(context, 'ship'), str):
            await context.send(embed_data)
        else:
            await menus.menu(context, pages=embed_data.pages, controls=embed_data.controls)

    @commands.command(name="alevent")
    async def chat_send_event_embed(self, context: Context):
        """This sends info about recent events"""
        embed = self.chat_get_embed(context, 'event')
        await menus.menu(context, pages=embed.pages, controls=embed.controls)

    @staticmethod
    def chat_get_embed(context: Context, type_: str):
        """
        Gets chat embed depending of the given type.
            Possible types: 'ship', 'item', 'event'
        """

        def extract_name(data: str) -> str:
            return unidecode(' '.join(re.findall(r'[^\s]+', data)[1:])).lower().strip()

        def find_similar_names(data: str, possibilities: Dict[str, str]) -> Tuple[str, ...]:
            return tuple(map(str, get_close_matches(word=data, possibilities=possibilities, n=3)))

        def format_similar_names(data: Tuple[str, ...]) -> str:
            return f"Did you mean {'any of these' if len(data) > 1 else 'this'} **{chat.humanize_list(data, style='or')}**?"

        type_ = type_.lower().strip()
        if type_ in ('ship', 'item'):
            names: Dict[str, str] = {}
            if type_ == 'ship':
                names = ship_names
            elif type_ == 'item':
                names = item_names

            if name := extract_name(context.message.content):
                if name not in names and name != "random":
                    if similar_names := find_similar_names(name, names):
                        return format_similar_names(similar_names)
                    return "Name either mistyped or nonexistent."

                if type_ == 'ship':
                    return ShipEmbed(name if name != "random" else choice(tuple(names.keys())))
                elif type_ == 'item':
                    return ItemEmbed(name if name != "random" else choice(tuple(names.keys())))
            return "Name was not specified."

        elif type_ == 'event':
            return EventEmbed()

        raise ValueError(f"Unhandled Type {type_}")
