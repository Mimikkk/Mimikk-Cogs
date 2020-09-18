from .ship_embed import get_api_data, create_select_controls, get_image_url, cargo_query
from .imports import *

item_names: Dict[str, str] = dict()


class ItemEmbed(object):
    def __init__(self, name: str):
        # Dummy Private Variables
        self.__menu_reactions: Tuple[str, ...] = tuple()
        self.__data: List[Dict[str, str]] = []
        self.__stars: Tuple[str, ...] = tuple()
        self.__image_url: str = ""
        self.__colors: Tuple[int, ...] = tuple()

        # Dummy Public Variables
        self.controls: Dict[str, Callable] = dict()
        self.pages: List[discord.Embed, ...] = []

        # Initialization
        self.__init_data(name)

        self.__init_pages()
        self.__init_controls()

    def __init_data(self, name: str):
        cargo_data = cargo_query(tables="equipment", fields=CONSTS.SQL.ITEM_TABLE_ALL_FIELDS.value,
                                 where=f"equipment.Name='{item_names[name]}'", limit="10")
        print(item_names[name], name, item_names)
        for dict_ in cargo_data.json():
            print(dict_)
            self.__data.append(dict(map(lambda x: (x, str(dict_[x])), dict_)))

        item_rarity = {'1': u'🥉', '2': u'🥈', '3': u'🥇', '4': u'🏅', '5': u'🎖', '6': u'🏆'}
        item_stars = {'1': u'NR-⭐', '2': u'NR-⭐⭐', '3': u'R-⭐⭐⭐',
                      '4': u'E-⭐⭐⭐⭐', '5': u'SR-⭐⭐⭐⭐⭐', '6': u'UR-⭐⭐⭐⭐⭐⭐'}
        item_colors = {'1': 0xCCCCCC, '2': 0xCCCCCC, '3': 0x41D7FF,
                       '4': 0xCC7BFF, '5': 0xFDC637, '6': 0xBD4000}

        rarities = (item_rarity[str(self.__data[i]['Stars'])] for i in range(len(self.__data)))
        self.__stars = tuple((item_stars[str(self.__data[i]['Stars'])] for i in range(len(self.__data))))
        self.__colors = tuple((item_colors[str(self.__data[i]['Stars'])] for i in range(len(self.__data))))
        self.__menu_reactions = (u'❌', *rarities, u'🗺')
        self.__image_url = get_image_url(self.__data[0]['Image'])

    def __init_pages(self):
        self.__page_stats()
        self.__page_drops()

    def __page_constructor(self, footer_desc: str, color: int, author_desc: str):
        return (discord.Embed(color=color)
                .set_author(name=author_desc, icon_url=self.__image_url)
                .set_thumbnail(url=self.__image_url)
                .set_footer(text=f"Page {len(self.pages) + 1} : {footer_desc}", icon_url=self.__image_url))

    def __page_stats(self):
        # self.__colors[i], f"{self.__data[i]['Name']} {self.__data[i]['Type']} {self.__stars[i]}"
        for i in range(len(self.__data)):  # hopefully they're in-order
            embed = self.__page_constructor(f"{self.__data[i]['Name']} {self.__data[i]['Type']} {self.__stars[i]}",
                                            self.__colors[i],
                                            f"Stats & Max Stats", )
            self.pages.append(embed)

    def __page_drops(self):
        embed = self.__page_constructor(f"{self.__data[0]['Name']} {self.__data[0]['Type']}",
                                        self.__colors[-1], f"Drops & Info", )

        self.pages.append(embed)

    def __init_controls(self):
        self.controls = create_select_controls(self.__menu_reactions)
