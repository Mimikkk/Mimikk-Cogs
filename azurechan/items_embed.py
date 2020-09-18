from .ship_embed import get_api_data, create_select_controls, get_image_url, cargo_query
from .imports import *

item_names: Dict[str, str] = dict()


class ItemEmbed(object):
    def __init__(self, name: str):
        # Dummy Private Variables
        self.__menu_reactions: Tuple[str, ...] = ()
        self.__data: List[Dict[str, str]] = []
        # Dummy Public Variables
        self.controls: Dict[str, Callable] = {}
        self.pages: List[discord.Embed] = []
        self.variants_count = 0
        # Pages

        # Stats
        # Stats Max
        # Map Drop Location / Used by

        # Initialization
        self.__init_data(name)

        self.__init_pages()
        self.__init_controls()

    def __init_data(self, name: str):
        cargo_data = cargo_query(tables="equipment", fields=CONSTS.SQL.ITEM_TABLE_ALL_FIELDS.value,
                                  where=f"equipment.Name='{item_names[name]}'", limit="10")
        self.__data = [dict(map(lambda x: (x, str(item[x])), item)) for item in cargo_data.json]
        self.__image_url: str = ""

        item_rarity = {'1': u'🥇', '2': u'🥈', '3': u'🥉', '4': u'🏅', '5': u'🎖', '6': u'🏆'}
        rarities = (item_rarity[str(self.__data[i]['Stars'])] for i in range(len(self.__data)))
        self.__menu_reactions = (u'❌', *rarities, u'🗺', u'ℹ')
        self.__image_url = get_image_url(self.__data[0]['Image'])

    def __init_pages(self):
        self.__page_stats()
        self.__page_drops()
        self.__page_info()

    def __page_constructor(self):
        pass

    def __page_stats(self):
        for i in range(len(self.__data)):   # hopefully they're in-order
            pass
        pass

    def __page_drops(self):
        pass

    def __page_info(self):
        pass

    def __init_controls(self):
        self.controls = create_select_controls(self.__menu_reactions)
