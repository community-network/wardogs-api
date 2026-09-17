import requests
from typing import TypedDict


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


async def get_player_summaries(api_key: str, steam_id: str) -> Player:
    url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}"
    response = requests.get(url)
    data: dict[str, dict[str, list[Player]]] = response.json()
    return data.get("response", {}).get("players", [])[0]
