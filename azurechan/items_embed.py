from .utils import get_api_data, create_select_controls, get_image_url, cargo_query, get_name_url, embed_url
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
            self.__data.append(dict(map(lambda x: (x, str(dict_[x])), dict_)))

        item_rarity = {'1': u'🥉', '2': u'🥈', '3': u'🥇', '4': u'🏅', '5': u'🎖', '6': u'🏆'}
        item_stars = {'1': u'N-⭐', '2': u'N-⭐⭐', '3': u'R-⭐⭐⭐',
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
        self.__menu_reactions = (u'❌', *rarities, u'ℹ')
        self.__image_url = get_image_url(self.__data[0]['Image'])
        self.__factor_notes()

    def __factor_notes(self):
        def format_link(str_: str):
            if len(link := str_.split('|', 1)) > 1:
                return embed_url(link[1], get_name_url(link[0]))
            return embed_url(link[0], get_name_url(link[0]))

        notes: Tuple[str, ...] = ("Notes", "DropLocation")
        for dict_ in self.__data:
            for note in notes:
                dict_[note] = re.sub(r'\[\[(.+?)]]', lambda g: format_link(g.group(1)), dict_[note])

    def __init_pages(self):
        self.__page_stats()
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

        emoji = {"PlaneHP": u'💞', "Health": u'❤', "Acc": u'🎯', "Damage": u'💥',
                 "Reload": u'♻', "AA": u'📡', "Torp": u'🥢', "Air": u'🛩',
                 "Speed": u'⏩', "Luck": u'🎱', "ASW": u'🛥', "Oxygen": u'☁', "Ammo": u'🎹',
                 "ConstructTime": u'🛠', "Firepower": u'🔥', "Aviation": u'🛩', "RoF": u'♻',
                 "Accuracy": u'🎯', "Torpedo": u'🥢', 'Tech': u'✨', "Evasion": u'👥',
                 'Notes': u'📄', 'DropLocation': "🗺", 'Bombs': u'💣'}

        stats = ("Health", "Torpedo", "Firepower", "Aviation",
                 "Evasion", "PlaneHP", "Reload", "ASW",
                 "Oxygen", "AA", "Luck", "Acc", "Spd")

        max_stats = ("HealthMax", "TorpMax", "FPMax", "AvMax",
                     "EvasionMax", "PlaneHPMax", "ReloadMax", "ASWMax",
                     "OxygenMax", "AAMax", "LuckMax", "AccMax", "SpdMax", "RoFMax",)

        for i in range(len(self.__data)):  # hopefully they're in-order
            embed = self.__page_constructor(f"{self.__data[0]['Nationality']} {self.__data[i]['Type']}",
                                            self.__colors[i],
                                            f"Stats & Max Stats, {self.__stars[i]}")

            has_stats: bool = False
            for (norm_, max_) in zip(stats, max_stats):
                if self.__data[i][norm_] in ' 0' and self.__data[i][max_] in ' 0': continue

                if not has_stats:
                    has_stats = True
                    embed.add_field(name="Stat Changes:", value='\u200b', inline=False)

                embed.add_field(name=f"{emoji[norm_]}: {self.__data[i][norm_]}"
                                     f"{' → ' + self.__data[i][max_] if self.__data[i][max_] else ''}",
                                value="\u200b", inline=True)

            specialized: Dict[str, str] = {}
            if self.__data[i]['Salvoes']:
                salvoes = self.__data[i]['Salvoes']
                shells = self.__data[i]['Shells']
                specialized[f"{emoji['Torp']} Volleys:"] = f"**{salvoes} x {shells}** shells"

            if self.__data[i]['Characteristic']:
                ammo = self.__data[i]["Ammo"] if self.__data[i]["Ammo"] else "Normal"
                character = self.__data[i]["Characteristic"] if self.__data[i]["Characteristic"] else "Normal"
                specialized[f"{emoji['Ammo']} Ammunition:"] = f"**{ammo}** Ammo with **{character}** Characteristic"

            if self.__data[i]['Angle']:
                angle = self.__data[i]['Angle']
                spread = self.__data[i]['Spread']
                range_ = self.__data[i]['WepRange']
                specialized[f"{emoji['Acc']} Angle and Spread:"] = (
                        f"**{angle}°**"
                        + f" ± **{spread}°**" * bool(spread)
                        + f" with the range of **{range_}**" * bool(range_))

            if self.__data[i]['PingFreq']:
                ping_freq = self.__data[i]['PingFreq']
                specialized[f"{emoji['AA']} Radar:"] = f"**{ping_freq}s** per swap"

            if self.__data[i]['AAGun1']:
                aa_gun1 = self.__data[i]['AAGun1']
                aa_gun2 = self.__data[i]['AAGun2']
                specialized[f"{emoji['AA']} Anti-Air Guns:"] = f"**{aa_gun1}**" + f" and **{aa_gun2}**" * bool(aa_gun2)

            if self.__data[i]['Bombs1']:
                bombs1 = self.__data[i]['Bombs1']
                bombs2 = self.__data[i]['Bombs2']
                specialized[f"{emoji['Bombs']} Bombs:"] = f"**{bombs1}**" + f" and **{bombs2}**" * bool(bombs2)

            if self.__data[i]['Damage']:
                dmg = self.__data[i]['Damage']
                max_dmg = self.__data[i]['DamageMax']
                rof = self.__data[i]['RoF']
                max_rof = self.__data[i]['RoFMax']
                volley_time = self.__data[i]['VolleyTime']
                salvoes = int(self.__data[i]['Salvoes']) if self.__data[i]['Salvoes'] else 0
                shells = int(self.__data[i]['Shells']) if self.__data[i]['Shells'] else 0
                projectiles = max(salvoes, shells, salvoes * shells)
                coef = self.__data[i]['Coef']

                specialized[f"{emoji['Damage']} Attack:"] = (
                        f"**{dmg} → {max_dmg}**"
                        + f" **x {projectiles}**" * bool(projectiles > 1)
                        + f" with rate of fire of **{rof}s → {max_rof}**s per volley" * bool(rof)
                        + f" at **{coef}%** Efficiency" * bool(coef)
                        + f" and action time of **{volley_time}s**" * bool(volley_time))

            for (stat_name, stat_format) in specialized.items():
                embed.add_field(name=stat_name, value=stat_format, inline=False)

            if self.__data[i]['Notes']:
                embed.add_field(name=f"{emoji['Notes']} Note:", value=self.__data[i]['Notes'], inline=False)

            drop_info = self.__data[i]['DropLocation'] if self.__data[i]['DropLocation'] else "Unknown"
            embed.add_field(name=f"{emoji['DropLocation']} Acquired:", value=drop_info, inline=False)

            self.pages.append(embed)

    def __page_usability(self):
        def format_class(class_type: str):
            return (f"{ship_classes[class_type]}-{class_type}",
                    f"{use_classes[class_type]} {self.__data[0][class_type + 'Note']}")

        embed = self.__page_constructor(f"{self.__data[0]['Nationality']} {self.__data[0]['Type']}",
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

    def __init_controls(self):
        self.controls = create_select_controls(self.__menu_reactions)
