from .ship_embed import get_api_data, create_select_controls, get_image_url, cargo_query, get_name_url
from .imports import *

item_names: Dict[str, str] = dict()


class ItemEmbed(object):
    def __init__(self, name: str):
        # Dummy Private Variables
        self.__name: str = ""
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

        for dict_ in cargo_data.json():
            print(dict_)
            self.__data.append(dict(map(lambda x: (x, str(dict_[x])), dict_)))

        item_rarity = {'1': u'🥉', '2': u'🥈', '3': u'🥇', '4': u'🏅', '5': u'🎖', '6': u'🏆'}
        item_stars = {'1': u'NR-⭐', '2': u'NR-⭐⭐', '3': u'R-⭐⭐⭐',
                      '4': u'E-⭐⭐⭐⭐', '5': u'SR-⭐⭐⭐⭐⭐', '6': u'UR-⭐⭐⭐⭐⭐⭐'}
        item_colors = {'1': 0xCCCCCC, '2': 0xCCCCCC, '3': 0x41D7FF,
                       '4': 0xCC7BFF, '5': 0xFDC637, '6': 0xBD4000}
        self.__name = self.__data[0]['Name'].replace("&quot;", "\"")

        item_misc_data = get_api_data(
            f"?action=parse&page={parse.quote(self.__name.replace(' ', '_'))}&prop=wikitext&format=json")

        item_misc_data = dict(re.findall(r' \| (AE.*) = (.+)', item_misc_data.json()['parse']['wikitext']['*']))
        for dict_ in self.__data:
            dict_['AE'] = '1' if item_misc_data.get('AE') else ''
            dict_['AENote'] = note if (note := item_misc_data.get('AENotes')) else ''

        rarities = (item_rarity[str(self.__data[i]['Stars'])] for i in range(len(self.__data)))
        self.__stars = tuple((item_stars[str(self.__data[i]['Stars'])] for i in range(len(self.__data))))
        self.__colors = tuple((item_colors[str(self.__data[i]['Stars'])] for i in range(len(self.__data))))
        self.__menu_reactions = (u'❌', *rarities, u'🗺', u'ℹ')
        self.__image_url = get_image_url(self.__data[0]['Image'])

    def __init_pages(self):
        self.__page_stats()
        self.__page_drops()
        self.__page_usability()

    def __page_constructor(self, author_desc: str, color: int, footer_desc: str):
        embed = (discord.Embed(color=color)
                 .set_author(name=author_desc, icon_url=self.__image_url)
                 .set_thumbnail(url=self.__image_url)
                 .set_footer(text=f"Page {len(self.pages) + 1} : {footer_desc}", icon_url=self.__image_url))
        embed.title = self.__name
        embed.url = get_name_url(self.__name)
        return embed

    def __page_stats(self):
        stats = {"Health": "Health", "Torpedo": "Torpedo", "Firepower": "Firepower",
                 "Aviation": "Aviation", "Evasion": "Evasion", "PlaneHP": "Plane Health",
                 "Reload": "Reload", "ASW": "ASW", "Oxygen": "Oxygen",
                 "AA": "Anti-Air", "Luck": "Luck", "Acc": "Accuracy", "Spd": "Speed",
                 "Damage": "Damage", "RoF": "Rate of Fire"}

        emoji = {"PlaneHP": u'💞', "Health": u'❤', "Acc": u'🎯', "Damage": u'💥',
                 "Reload": u'♻', "AA": u'📡', "Torp": u'🥢', "Air": u'🛩',
                 "Speed": u'⏩', "Luck": u'🎱', "ASW": u'🛥', "Oxygen": u'☁', "Ammo": u'🎹',
                 "ConstructTime": u'🛠', "Firepower": u'🔥', "Aviation": u'🛩', "RoF": u'♻',
                 "Accuracy": u'🎯', "Torpedo": u'🥢', 'Tech': u'✨', "Evasion": u'👥',
                 'Notes': u'📄'}

        max_stats = ("HealthMax", "TorpMax", "FPMax", "AvMax",
                     "EvasionMax", "PlaneHPMax", "ReloadMax", "ASWMax",
                     "OxygenMax", "AAMax", "LuckMax", "AccMax", "SpdMax",
                     "DamageMax", "RoFMax",)

        for i in range(len(self.__data)):  # hopefully they're in-order
            embed = self.__page_constructor(f"{self.__data[i]['Type']}",
                                            self.__colors[i],
                                            f"Stats & Max Stats, {self.__stars[i]}")

            for (norm_, max_) in zip(stats, max_stats):
                if self.__data[0][norm_] in ' 0': continue
                embed.add_field(name=f"{emoji[norm_]}: {self.__data[i][norm_]}"
                                     f"{u' ⏩ ' + self.__data[i][max_] if self.__data[i][max_] else ''}",
                                value="\u200b", inline=True)

            special_stats = ('Number', 'Spread', 'Angle',
                             'WepRange', 'Shells', 'Salvoes',
                             'Characteristic', 'PingFreq', 'VolleyTime',
                             'Coef', 'Ammo', 'AAGun1', 'AAGun2', 'Bombs1', 'Bombs2')

            for stat in special_stats:
                embed.add_field(name="", value="", inline=True)

            if self.__data[i]['Notes']:
                embed.add_field(name="Note:", value=self.__data[i]['Notes'], inline=False)

            self.pages.append(embed)

    """
    {'Name': 'Autoloader', 'Image': '2200.png', 'Type': 'Auxiliary', 'Stars': 4, 
     'Nationality': 'Universal', 'Tech': 'T3', 'Health': '', 'HealthMax': '', 
     'Torpedo': '', 'TorpMax': '', 'Firepower': 3, 'FPMax': 7, 'Aviation': '', 
     'AvMax': '', 'Evasion': '', 'EvasionMax': '', 'PlaneHP': '', 'PlaneHPMax': '', 
     'Reload': '', 'ReloadMax': '', 'ASW': '', 'ASWMax': '', 'Oxygen': '', 
     'OxygenMax': '', 'AA': '', 'AAMax': '', 'Luck': '',
     'LuckMax': '', 'Acc': '', 'AccMax': '', 'Spd': '', 'SpdMax': '', 'Damage': '', 
     'DamageMax': '', 'RoF': 14, 'RoFMax': 35, 'Number': '', 'Spread': '', 'Angle': '', 
     'WepRange': '', 'Shells': '', 'Salvoes': '','Characteristic': '', 'PingFreq': '', 
     'VolleyTime': '', 'Coef': '', 'Ammo': '', 'AAGun1': '', 'AAGun2': '',
     'Bombs1': '', 'Bombs2': '', 'DD': 1, 'DDNote': '', 'CL': 1, 'CLNote': '', 
     'CA': 1, 'CANote': '', 'CB': 1, 'CBNote': '', 'BM': 1, 'BMNote': '', 'BB': 1, 
     'BBNote': '', 'BC': 1, 'BCNote': '', 'BBV': 1, 'BBVNote': '', 'CV': '', 'CVNote': '', 
     'CVL': '', 'CVLNote': '', 'AR': 1, 'ARNote': '', 'SS': 1, 'SSNote': '', 'SSV': '',
     'SSVNote': '', 'DropLocation': '[[6-3]], [[10-1]], [[11-3]], Any T3/4 Tech box', 
     'Notes': ''}
     """

    def __page_usability(self):
        def format_class(class_type: str):
            return (f"{ship_classes[class_type]}-{class_type}",
                    f"{use_classes[class_type]} {self.__data[0][class_type + 'Note']}")

        embed = self.__page_constructor(f"{self.__data[0]['Type']}",
                                        self.__colors[-1],
                                        f"Usability")

        ship_classes = {"DD": "Destroyer", "CL": "Light Cruiser", "CA": "Heavy Cruiser",
                        "CB": "Large Cruiser", "BM": "Monitor", "BB": "Battleship",
                        "BC": "Battlecruiser", "BBV": "Aviation Battleship", "CV": "Aircraft Carrier",
                        "CVL": "Light Aircraft Carrier", "AR": "Repair Ship", "SS": "Submarine",
                        "SSV": "Submarine Carrier", "AE": "Munition"}

        use_classes = {}
        for class_ in ship_classes:
            use_classes[class_] = (u'✅' if self.__data[0][class_] == '1'
                                   else (u'☑' if self.__data[0][class_] == '2' else u'❌'))

        embed.add_field(name="Used By:", value="\u200b", inline=False)
        for class_ in use_classes:
            name, value = format_class(class_)
            embed.add_field(name=name, value=value, inline=False)
        self.pages.append(embed)

    def __page_drops(self):
        embed = self.__page_constructor(f"{self.__data[0]['Type']}",
                                        self.__colors[-1],
                                        f"Drops")

        self.pages.append(embed)

    def __init_controls(self):
        self.controls = create_select_controls(self.__menu_reactions)
