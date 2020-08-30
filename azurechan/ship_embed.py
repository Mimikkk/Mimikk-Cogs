from urllib import parse
from .imports import *

ship_names: Dict[str, str] = dict()


class ShipEmbed(object):
    """This Creates Ship Embed Menu using data from azur lane wiki"""

    def __init__(self, name: str):

        # Dummy Private Variables
        self.__data: Dict[str, Any] = {}
        self.__menu_reactions: str = ""
        self.__menu_types: Tuple[str, ...] = ()
        self.__is_retrofit: bool = False
        self.__is_tech: bool = False

        # Dummy Public Variables
        self.controls: Dict[str, Callable] = {}
        self.pages: List[discord.Embed] = []

        # Initialization
        self.__init_wiki_data(name)
        self.__init_ship_data()
        self.__init_ship_images()

        self.__init_controls()
        self.__init_pages()

    def __init_wiki_data(self, name):
        """Some fancy way to get the data from MediaWiki"""

        # Get data from a cargo table with ship data
        ship_data = cargo_query(tables="ships", fields=CONSTS.SQL.SHIP_TABLE_ALL_FIELDS.value,
                                where=f"ships.Name='{ship_names[name]}'", limit="1")
        data: Dict[str, str]
        for data in ship_data.json():
            self.__data = dict(map(lambda x: (x, str(data[x])), data))

        # Get the rest of data needed which isn't directly in the cargo table
        ship_misc_data = get_api_data(f"?action=parse&page={self.__data['Name']}&prop=wikitext&format=json")
        ship_misc_data = dict(
            re.findall(r' \| (Skill.+|Type\d|StatBonus.+|TechP.+|Reinforce.+|Scrap.+|B\d+|D.+) = (.+)',
                       ship_misc_data.json()['parse']['wikitext']['*']))

        self.__data.update(ship_misc_data)

    def __init_ship_images(self):
        """This Supplies Image URLs of the Ship"""
        for image_name in self.__images_types:
            self.__data[f'{image_name}_url'] = get_image_url(self.__data[image_name])

    def __init_ship_data(self):
        """This initializes data used by the ShipEmbed"""

        # Checks if is retrofit based on presence of Retrofit image b/c wiki data is Borked as per usual
        self.__is_retrofit = bool(self.__data['ImageKai'])
        self.__is_tech = bool('B5' in self.__data)

        self.__menu_reactions = (CONSTS.SHIP.RETROFIT.MENU_REACTIONS.value if self.__is_retrofit
                                 else CONSTS.SHIP.NORMAL.MENU_REACTIONS.value)
        self.__menu_types = (CONSTS.SHIP.RETROFIT.MENU_TYPES.value if self.__is_retrofit
                             else CONSTS.SHIP.NORMAL.MENU_TYPES.value)
        self.__images_types = (CONSTS.SHIP.RETROFIT.IMAGES.value if self.__is_retrofit
                               else CONSTS.SHIP.NORMAL.IMAGES.value)

    def __init_controls(self):
        """Creates Menu based on reactions on retrofit option"""
        self.controls = create_select_controls(self.__menu_reactions)

    def __init_pages(self):
        """Gets all the pages in embed form"""
        self.__page_stats()
        self.__page_skills()
        self.__page_limit_break()
        self.__page_equipment()
        self.__page_drops_table()
        self.__page_card_info()

    def __page_constructor(self,
                           footer_desc: str,
                           is_retrofit_variant: bool = False,
                           has_banner: bool = False,
                           has_splashart: bool = False) -> discord.Embed:
        """Construct Page's Default Data like Thumbnail, Banner, Author, and Footer"""

        def format_color() -> int:
            return CONSTS.SHIP.RARITY.COLORS.value[self.get_rarity(is_retrofit_variant=is_retrofit_variant)]

        def format_url(image_type: str) -> str:
            return self.__data[f"{image_type}{'Kai' if is_retrofit_variant else ''}_url"]

        embed = (discord.Embed(color=format_color())
                 .set_author(name=f"{self.__data['Name']} {self.__data['Type']}",
                             icon_url=format_url("ImageShipyardIcon"))
                 .set_thumbnail(url=format_url("ImageIcon"))
                 .set_footer(text=f"Page {len(self.pages) + 1} : {footer_desc}", icon_url=format_url("ImageChibi")))

        if has_banner:
            embed.set_image(url=format_url("ImageBanner"))
        elif has_splashart:
            embed.set_image(url=format_url("Image"))

        return embed

    def __page_stats(self):
        """Stats Pages Constructor either 1-3 or 1-5 pages, depends whether the ship has a retrofit option"""

        def format_stat() -> str:
            return val if (val := self.__data[get_stat()]) != '0' else "Not in Use"

        def get_stat() -> str:
            # Look at me I'm special, I can be Kai...
            if i > 3 and stat in ("Speed", "Armor"):
                return f"{CONSTS.SHIP.STATS.FORMAT.value[stat]}Kai"

            # Look at me I'm special, I don't change...
            if stat in ("Speed", "Luck", "Construction", "Armor"):
                return f"{CONSTS.SHIP.STATS.FORMAT.value[stat]}"
            return f"{CONSTS.SHIP.STATS.FORMAT.value[stat]}{CONSTS.SHIP.STAT_TYPES.value[type_]}"

        # if index > 3 it means it's retrofit variant of the page
        i: int
        type_: str
        embed: discord.Embed
        for (i, type_) in enumerate(self.__menu_types, 1):
            embed = self.__page_constructor(type_, is_retrofit_variant=i > 3, has_banner=True)

            for stat in CONSTS.SHIP.STATS.TYPES.value:
                embed.add_field(name=f'{get_emoji(stat)} - {stat}', value=format_stat(), inline=True)

            self.pages.append(embed)

    def __page_skills(self):
        """Skill Page creator either 4 or 6, depends whether the ship has a retrofit option"""
        embed = self.__page_constructor("Skills", has_banner=True)
        embed.add_field(name=u"🕯Skills🕯", value="\u200b", inline=False)

        def format_description():
            return re.sub(r'\[\[(.*?)]]', lambda g: g.group(1), self.__data[f'Skill{i}Desc'])

        # There are only 5 skill max in Azure Lane per ship, currently that is

        for (i, emoji) in enumerate((u'1️⃣', u'2️⃣', u'3️⃣', u'4️⃣', u'5️⃣'), 1):
            if not self.__data.get(f'Skill{i}'): break
            embed.add_field(name=f"{emoji} - {self.__data[f'Skill{i}']} - {self.__data[f'Type{i}']}",
                            value=format_description(), inline=False)

        self.pages.append(embed)

    def __page_limit_break(self):
        """Page containing info about limit breaks xor strengthens, either 7, or 8 page"""

        def format_lb(n: int) -> str:
            return '\n'.join(map(lambda x: '• ' + x, lb.split(' / '))) if (lb := self.__data[f'LB{n}']) else "\u200b"

        def format_tooltips(str_: str) -> str:
            return re.sub(r'{{Tooltip\|(.+?)\|.+?}}', lambda g: g.group(1), str_)

        def listify_strengthen(n: int) -> str:
            return re.sub(r'{{(.+?)\}\}',
                          lambda g: get_emoji(g.group(1)),
                          re.sub(r'(</?li>(</?li>)?)', ';', format_tooltips(self.__data[f'B{n}'])).strip(';'))

        def format_strengthen(n: int) -> str:
            return '\n'.join(map(lambda x: '• ' + x,
                                 filter(lambda x: bool(x.strip()), listify_strengthen(n).split(';'))))

        embed = self.__page_constructor("Limit Breaks", has_banner=True)

        formats_ = (
            u'1️⃣ - First - 5', u'2️⃣ - Second - 10', u'3️⃣ - Third - 15', u'4️⃣ - Forth - 20', u'5️⃣ - Fifth - 25',
            u'6️⃣ - Sixth - 30')
        if self.__is_tech:
            embed.add_field(name=u"🏵Strengthen Level🏵", value="\u200b", inline=False)
            for (level, format_) in zip(range(5, 31, 5), formats_):
                embed.add_field(name=format_, value=format_strengthen(level), inline=False)

        else:
            embed.add_field(name=u"🏵Limit Break🏵", value="\u200b", inline=False)

            embed.add_field(name="1️⃣ - First", value=format_lb(1), inline=False)
            embed.add_field(name="2️⃣ - Second", value=format_lb(2), inline=False)
            embed.add_field(name="3️⃣ - Third", value=format_lb(3), inline=False)

        self.pages.append(embed)

    def __page_equipment(self):
        """Page containing info about equipment and misc, either 6, or 8 page"""

        def format_eq_eff(eq_slot: int) -> str:
            return (f"{self.__data[f'Eq{eq_slot}EffInit']} {u'▶'} {self.__data[f'Eq{eq_slot}EffInitMax']}"
                    + self.__is_retrofit * f" {u'⏩'} {self.__data[f'Eq{eq_slot}EffInitKai']}")

        def format_icons(str_: str) -> str:
            return re.sub(r'{{(.+?)\}\}', lambda g: get_emoji(g.group(1)), str_)

        def format_tooltips(str_: str) -> str:
            return format_icons(re.sub(r'{{Tooltip\|(.+?)\|.+?}}', lambda g: g.group(1), str_))

        embed = self.__page_constructor("Equipment & Misc.", has_banner=True)
        embed.add_field(name=u"🏹Equipment🏹", value=u"\u200b", inline=False)
        embed.add_field(name=f"{u'1️⃣'} {self.__data['Eq1Type']}", value=format_eq_eff(1), inline=False)
        embed.add_field(name=f"{u'2️⃣'} {self.__data['Eq2Type']}", value=format_eq_eff(2), inline=False)
        embed.add_field(name=f"{u'3️⃣'} {self.__data['Eq3Type']}", value=format_eq_eff(3), inline=False)

        embed.add_field(name=u"⚙Misc.⚙", value=u"\u200b", inline=False)
        embed.add_field(name=u"⛏ - Scrap Value",
                        value=format_tooltips(self.__data['ScrapIncome'])
                        if self.__data.get('ScrapIncome') else "This ship cannot be scrapped",
                        inline=False)

        embed.add_field(name=u"✨ - Enhance Value",
                        value=format_tooltips(self.__data['ReinforcementValue'])
                        if self.__data.get('ReinforcementValue') else "This ship cannot be used to enhance",
                        inline=False)

        if self.__data.get('StatBonusCollect'):
            embed.add_field(name=u"🧖‍♀️ - Collection Bonus",
                            value=f"{self.__data['StatBonusCollect']} {get_emoji(self.__data['StatBonusCollectType'])} "
                                  f"+ {self.__data['TechPointCollect']} {get_emoji('Tech')}", inline=False)
            embed.add_field(name=u"🏵 - Max Limit Break Bonus",
                            value=f"{self.__data['TechPointMLB']} {get_emoji('Tech')}", inline=False)
            embed.add_field(name=u"🎓 - Max Cognitive Level Bonus",
                            value=f"{self.__data['StatBonus120']} {get_emoji(self.__data['StatBonus120Type'])} "
                                  f"+ {self.__data['TechPoint120']} {get_emoji('Tech')}", inline=False)
        else:
            embed.add_field(name=u"Collection Bonus", value="Does not provide bonuses", inline=False)

        self.pages.append(embed)

    def __page_drops_table(self):
        """Drops Page creator, either 7 or 9, depends whether the ship has a retrofit option"""
        embed = self.__page_constructor("Drop Locations", has_banner=True)

        def format_note() -> str:
            def maybe_link_embed(str_: str):
                (page_name, *name) = str_.split('|', 1)
                return embed_url(name[0] if len(name)>0 else page_name, get_name_url(page_name))

            return re.sub(r'{{(.+?)\}\}', lambda g: get_emoji(g.group(1)),
                          re.sub(r'\[\[(.+?)]]', lambda g: maybe_link_embed(g.group(1)), self.__data['DropNote']))

        drops = {}
        drop_type = ""
        drop_note: str = ""
        is_drop: bool = False
        is_exchange: bool = False
        for key in filter(lambda x: x.startswith("D"), self.__data.keys()):
            if key == "DropNote": drop_note = format_note()
            elif key == "DExchange":
                is_exchange = True
            elif match := re.match(r'D([A-Z][a-z]+)', key):
                if match.group(1) in ('Light', 'Heavy', 'Special', 'Limited'):
                    drop_type = match.group(1)
                    is_drop = True

            elif match := re.match(r'D(\d+?)-(\d+)', key):
                (map_, level) = match.group(1), match.group(2)
                if map_ not in drops: drops[map_] = []
                drops[map_].append(level)

        for map_ in drops: drops[map_] = chat.humanize_list(drops[map_])

        embed.add_field(name="🛠Construction info🛠",
                        value=f"Time: **{self.__data['ConstructTime']}** Type: **{drop_type}**"
                        if is_drop else self.__data['ConstructTime'],
                        inline=False)

        embed.add_field(name="🗺Map Location🗺", value="\u200b" if drops else "Doesn't drop on any map.", inline=False)

        for map_ in drops: embed.add_field(name=f"Map: {map_}", value=f"levels: **{drops[map_]}**", inline=True)
        if drop_note:
            embed.add_field(name=f"✨{'Exchange' if is_exchange else 'Event'} info✨", value=drop_note, inline=False)

        self.pages.append(embed)

    def __page_card_info(self, is_retrofit_variant: bool = False):
        """Info Page creator, either 8 or 10 and 11, depends whether the ship has a retrofit option"""

        def maybe_extract_url(str_: str) -> str:
            name: str = val if (val := self.__data[str_]) else u'\u200b'
            html_url: str = ""

            if '[[' in name:
                (wiki_page, name) = name.lstrip('[').rstrip(']').split('|', 1)
                html_url = f"{CONSTS.SQL.WIKIPEDIA_URL.value}{wiki_page.split(':')[-1]}"

            elif '[' in name:
                (html_url, name) = name.lstrip('[').rstrip(']').split(' ', 1)

            return embed_url(name, html_url) if html_url and name != u'\u200b' else name

        def format_rarity() -> str:
            return CONSTS.SHIP.RARITY.FORMAT.value[self.get_rarity(is_retrofit_variant)]

        embed = self.__page_constructor("Card Info", has_splashart=True, is_retrofit_variant=is_retrofit_variant)

        embed.add_field(name="✨ - Nation", value=maybe_extract_url('Nationality'), inline=True)
        embed.add_field(name="🎓 - Class", value=maybe_extract_url('Class'), inline=True)
        embed.add_field(name=f"💎 - Rarity - {self.get_rarity(is_retrofit_variant)}", value=format_rarity(), inline=True)

        embed.add_field(name="✍ - Artist", value=maybe_extract_url("Artist"), inline=True)
        embed.add_field(name="🐦 - Twitter", value=maybe_extract_url("ArtistTwitter"), inline=True)
        embed.add_field(name="🖌 - Pixiv", value=maybe_extract_url("ArtistPixiv"), inline=True)

        embed.add_field(name="🎤 - VA", value=maybe_extract_url("VA"), inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name="📄 - Wikipage",
                        value=embed_url(self.__data['Name'], get_name_url(self.__data['Name'])), inline=True)
        self.pages.append(embed)

        if self.__is_retrofit and not is_retrofit_variant: self.__page_card_info(is_retrofit_variant=True)

    def get_rarity(self, is_retrofit_variant: bool = False) -> str:
        return (CONSTS.SHIP.RETROFIT.RARITY.value[self.__data['Rarity']]
                if is_retrofit_variant else self.__data['Rarity'])


def create_select_controls(reactions):
    """Creates Menu's Reaction Based Navigation"""

    async def select_page(ctx, pages, controls, message, page, timeout, emoji):
        # if can manage messages remove the react
        if message.channel.permissions_for(ctx.me).manage_messages:
            with contextlib.suppress(discord.NotFound): await message.remove_reaction(emoji, ctx.author)
        return await menus.menu(ctx, pages, controls, message=message, page=page, timeout=timeout)

    def wrap(func, num: int):
        async def wrapper(*args):
            args = list(args)
            args[4] = num
            return await func(*args)

        return wrapper

    # could use old good '< x >' keys
    # self.controls = menus.DEFAULT_CONTROLS
    _select: Callable[[int], Callable] = lambda num: wrap(select_page, num)
    return {emoji: menus.close_menu if i == -1 else _select(i) for (i, emoji) in enumerate(reactions, -1)}


def cargo_query(tables: str = "", fields: str = "", where: str = "", limit: str = "50", output_format: str = "json",
                api_url: str = "https://azurlane.koumakan.jp/w/index.php?"):
    return requests.get(url=api_url + "title=Special:CargoExport"
                                      f"&tables={tables}&fields={fields}&where={where}"
                                      f"&limit={limit}&format={output_format}")


def get_api_data(action: str, api_url: str = "https://azurlane.koumakan.jp/w/api.php") -> requests.Response:
    return requests.get(url=api_url + action)


def get_image_url(image_name: str, api_url: str = "https://azurlane.koumakan.jp") -> str:
    return f'{api_url}/Special:Redirect/file/{parse.quote(image_name.replace(" ", "_"))}?width=800'


def get_name_url(name: str, api_url: str = "https://azurlane.koumakan.jp") -> str:
    return f'{api_url}/{parse.quote(name.replace(" ", "_"))}'

def get_emoji(stat: str) -> str:
    return CONSTS.SHIP.STATS.EMOJI.value[stat]

def embed_url(name: str, link: str) -> str:
    return f"[{name}]({link.replace(' ', '_')})"
