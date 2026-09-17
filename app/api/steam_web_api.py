import aiohttp
from typing import TypedDict

from app.api import Singleton


class Player(TypedDict):
    steamid: str
    communityvisibilitystate: int
    profilestate: int
    personaname: str
    profileurl: str
    avatar: str
    avatarmedium: str
    avatarfull: str
    avatarhash: str
    personastate: int
    realname: str
    primaryclanid: str
    timecreated: int
    personastateflags: int
    loccountrycode: str
    locstatecode: str
    loccityid: int


class SteamWebClient(metaclass=Singleton):
    session: aiohttp.ClientSession

    async def async_init__(self):
        self.session = aiohttp.ClientSession()

    async def get_player_summaries(self, api_key: str, steam_id: str) -> Player:
        url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}"
        response = await self.session.get(url)
        data: dict[str, dict[str, list[Player]]] = await response.json()
        return data.get("response", {}).get("players", [])[0]
