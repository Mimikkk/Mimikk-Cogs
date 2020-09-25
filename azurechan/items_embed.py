from .utils import get_api_data, create_select_controls, get_image_url, cargo_query, get_name_url, embed_url, get_emoji
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

        self.__name = self.__data[0]['Name'].replace("&quot;", "\"")
        item_misc_data = \
            get_api_data(f"?action=parse&page={parse.quote(self.__name.replace(' ', '_'))}&prop=wikitext&format=json")

        item_misc_data = dict(re.findall(r' ?\| ?(AE.*|All) ?= ?(.+)', item_misc_data.json()['parse']['wikitext']['*']))
        for dict_ in self.__data:
            dict_['All'] = '1' if item_misc_data.get('All') else ''
            dict_['AE'] = '1' if item_misc_data.get('AE') else ''
            dict_['AENote'] = note if (note := item_misc_data.get('AENotes')) else ''

        rarities = (CONSTS.ITEM.RARITY_EMOJI.value[self.__data[i]['Stars']] for i in range(len(self.__data)))
        self.__stars = tuple((CONSTS.ITEM.STARS.value[self.__data[i]['Stars']] for i in range(len(self.__data))))
        self.__colors = tuple((CONSTS.ITEM.COLOR.value[self.__data[i]['Stars']] for i in range(len(self.__data))))
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
                dict_[note] = re.sub(r'\[\[(.+?)]]', lambda g: format_link(g.group(1)),
                                     dict_[note].replace("&lt;br&gt;", "\n").replace("&lt;br/&gt;", "\n").replace('&quot;', '"').replace('&amp;', '&'))

    def __init_pages(self):
        self.__page_stats()
        self.__page_usability()

    def __page_constructor(self, color: int, footer_desc: str):
        embed = (discord.Embed(color=color)
                 .set_author(name=f"{self.__data[0]['Nationality']} {self.__data[0]['Type']}", icon_url=self.__image_url)
                 .set_thumbnail(url=self.__image_url)
                 .set_footer(text=f"Page {len(self.pages) + 1} : {footer_desc}", icon_url=self.__image_url))
        embed.title = self.__name
        embed.url = get_name_url(self.__name)
        return embed

    def __page_stats(self):

        for i in range(len(self.__data)):  # hopefully they're in-order
            embed = self.__page_constructor(self.__colors[i], f"Stats & Max Stats, {self.__stars[i]}")

            has_stats: bool = False
            for (norm_, max_) in zip(CONSTS.ITEM.BASE_STATS.value, CONSTS.ITEM.MAX_STATS.value):
                if self.__data[i][norm_] in ' 0' and self.__data[i][max_] in ' 0': continue

                if not has_stats:
                    has_stats = True
                    embed.add_field(name="Stat Changes:", value='\u200b', inline=False)

                embed.add_field(name=f"{get_emoji(norm_)}: {self.__data[i][norm_]}"
                                     f"{' → ' + self.__data[i][max_] if self.__data[i][max_] else ''}",
                                value="\u200b", inline=True)

            specialized: Dict[str, str] = {}
            if self.__data[i]['Salvoes']:
                salvoes = self.__data[i]['Salvoes']
                shells = self.__data[i]['Shells']
                specialized[f"{get_emoji('Torp')} Volleys:"] = f"**{salvoes} x {shells}** shells"

            if self.__data[i]['Characteristic']:
                ammo = self.__data[i]["Ammo"] if self.__data[i]["Ammo"] else "Normal"
                character = self.__data[i]["Characteristic"] if self.__data[i]["Characteristic"] else "Normal"
                specialized[f"{get_emoji('Ammo')} Ammunition:"] = f"**{ammo}** Ammo with **{character}** Characteristic"

            if self.__data[i]['Angle']:
                angle = self.__data[i]['Angle']
                spread = self.__data[i]['Spread']
                range_ = self.__data[i]['WepRange']
                specialized[f"{get_emoji('Acc')} Angle and Spread:"] = (
                        f"**{angle}°**"
                        + f" ± **{spread}°**" * bool(spread)
                        + f" with the range of **{range_}**" * bool(range_))

            if self.__data[i]['PingFreq']:
                ping_freq = self.__data[i]['PingFreq']
                specialized[f"{get_emoji('AA')} Radar:"] = f"**{ping_freq}s** per swap"

            if self.__data[i]['AAGun1']:
                aa_gun1 = self.__data[i]['AAGun1']
                aa_gun2 = self.__data[i]['AAGun2']
                specialized[f"{get_emoji('AA')} Anti-Air Guns:"] = f"**{aa_gun1}**" + f" and **{aa_gun2}**" * bool(aa_gun2)

            if self.__data[i]['Bombs1']:
                bombs1 = self.__data[i]['Bombs1']
                bombs2 = self.__data[i]['Bombs2']
                specialized[f"{get_emoji('Bombs')} Bombs:"] = f"**{bombs1}**" + f" and **{bombs2}**" * bool(bombs2)

            if self.__data[i]['Damage']:
                dmg = self.__data[i]['Damage']
                max_dmg = self.__data[i]['DamageMax']
                rof = self.__data[i]['RoF']
                max_rof = self.__data[i]['RoFMax']
                volley_time = self.__data[i]['VolleyTime']
                coef = self.__data[i]['Coef']

                specialized[f"{get_emoji('Damage')} Attack:"] = (
                        f"**{dmg} → {max_dmg}**"
                        + f" with rate of fire of **{rof}s → {max_rof}**s per volley" * bool(rof)
                        + f" at **{coef}%** Efficiency" * bool(coef)
                        + f" and action time of **{volley_time}s**" * bool(volley_time))

            for (stat_name, stat_format) in specialized.items():
                embed.add_field(name=stat_name, value=stat_format, inline=False)

            if self.__data[i]['Notes']:
                embed.add_field(name=f"{get_emoji('Notes')} Note:", value=self.__data[i]['Notes'], inline=False)

            drop_info = self.__data[i]['DropLocation'] if self.__data[i]['DropLocation'] else "Unknown"
            embed.add_field(name=f"{get_emoji('DropLocation')} Acquired:", value=drop_info, inline=False)

            self.pages.append(embed)

    def __page_usability(self):
        embed = self.__page_constructor(self.__colors[-1], "Usability")

        use_classes = {}
        for class_ in CONSTS.SHIP.CLASSES.value:
            use_classes[class_] = \
                (u'✅' if self.__data[0][class_] == '1' or self.__data[0]['All'] == '1' else (u'☑' if self.__data[0][class_] == '2' else u'❌'))

        embed.add_field(name="Used By:", value="\u200b", inline=False)
        for class_ in use_classes:
            embed.add_field(name=f"{CONSTS.SHIP.CLASSES.value[class_]}-{class_}",
                            value=f"{use_classes[class_]} {self.__data[0][class_ + 'Note']}",
                            inline=False)
        self.pages.append(embed)

    def __init_controls(self):
        self.controls = create_select_controls(self.__menu_reactions)
