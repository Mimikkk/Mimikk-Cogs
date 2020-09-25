from .imports import *


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
                api_url: str = "https://azurlane.koumakan.jp/w/index.php?",
                offset: str = "0"):
    return requests.get(url=api_url + "title=Special:CargoExport"
                                      f"&tables={tables}&fields={fields}&where={where}"
                                      f"&offset={offset}&limit={limit}&format={output_format}")

def get_api_data(action: str, api_url: str = "https://azurlane.koumakan.jp/w/api.php") -> requests.Response:
    return requests.get(url=api_url + action)

def get_image_url(image_name: str, api_url: str = "https://azurlane.koumakan.jp") -> str:
    return (f'{api_url}/Special:Redirect/file/'
            f'{parse.quote(image_name.replace(" ", "_") if image_name.endswith(".png") else (image_name+".png").replace(" ", "_"))}?width=800')

def get_name_url(name: str, api_url: str = "https://azurlane.koumakan.jp") -> str:
    return f'{api_url}/{parse.quote(name.replace(" ", "_"))}'

def get_emoji(stat: str) -> str:
    return CONSTS.EMOJI.value[stat]

def embed_url(name: str, link: str) -> str:
    return f"[{name}]({link.replace(' ', '_')})"
