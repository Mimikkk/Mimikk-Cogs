from urllib import parse
from .ship_embed import get_api_data, create_select_controls, get_image_url
from .imports import *


class EventEmbed(object):
    def __init__(self):
        # Dummy Private Variables
        self.__menu_reactions: Tuple[str, ...] = ()

        # Dummy Public Variables
        self.controls: Dict[str, Callable] = {}
        self.pages: List[discord.Embed] = []
        self.en_news: Dict[str, str] = {}
        self.jp_cn_news: Dict[str, str] = {}

        # Initialization
        self.__init_data()

        self.__init_controls()
        self.__init_pages()

    def __init_data(self):
        news_data = get_api_data(action="?action=parse&page=Azur_Lane_Wiki&prop=wikitext&format=json")
        self.english_news = dict(re.findall(r'{{NewsItemEN((.|\n)+?)}}', news_data.json()["parse"]["wikitext"]["*"]))
        self.jp_cn_news = dict(re.findall(r'{{NewsItemJP((.|\n)+?)}}', news_data.json()["parse"]["wikitext"]["*"]))
        self.__menu_reactions = (u'❌', u'🇬🇧', u'🇯🇵')

    def __init_pages(self):
        self.__page_news(server_color=0x10108F, server_title="English",
                         image_ship="Enterprise", news=self.english_news)
        self.__page_news(server_color=0x8F1010, server_title="Japanese/Chinese",
                         image_ship="Akagi", news=self.jp_cn_news)

    def __page_news(self, server_color: int, image_ship: str, server_title: str, news: Dict[str, str]):
        def get_link(str_: str, api_url: str="https://azurlane.koumakan.jp/") -> str:
            return f"{api_url}{parse.quote(str_.replace(' ', '_'))}"

        embed = (discord.Embed(color=server_color)
                 .set_author(name="Azure Lane News", icon_url=get_image_url(f"{image_ship}Chibi.png"))
                 .set_thumbnail(url=get_image_url(f"{image_ship}Icon.png"))
                 .set_footer(text=f"{server_title} Server News", icon_url=get_image_url(f"{image_ship}Chibi.png"))
                 )

        news_feed: Iterable = map(lambda data: dict(re.findall(r'\| (.+?) = (.+)', data)), news)
        for (emoji, news) in zip((u'1️⃣', u'2️⃣', u'3️⃣', u'4️⃣', u'5️⃣', u'6️⃣'), news_feed):
            date = f"{news['day']}/{news['month']}."
            embed.add_field(
                name=f"{emoji} {news['title']} {f'from {date}' if news['type'] == 'event' else ''}"
                , value=f"[Link to {news['type']}]({get_link(news['link'])})\nInfo: {news['message']}", inline=False)

        self.pages.append(embed)

    def __init_controls(self):
        self.controls = create_select_controls(self.__menu_reactions)
