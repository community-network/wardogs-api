import logging
from logging.config import dictConfig
import time
import urllib.parse as urlparse
from urllib.parse import urlencode
import aiohttp
import jwt
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import RedirectResponse

from app.api.steam_web_api import SteamWebClient
from app.api.steam_login import SteamClient
from app.api.wardogs_models import PlayerStats
from app.config import LogConfig, PackagePathFilter, load_config
from app.database.connection import DatabaseSingleton
from app.database.functions import discord_user, stats_snapshot, wardogs_account

dictConfig(LogConfig().model_dump())

logger = logging.getLogger("api")
logger.addFilter(PackagePathFilter())

env_config = load_config()

db = DatabaseSingleton(env_config.db)


steam_client = SteamClient()
steam_web_client = SteamWebClient()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db()
    await steam_client.async_init__()
    await steam_web_client.async_init__()
    logger.info("Startup complete")
    yield
    logger.info("Shutting down...")
    await db.close_async()
    await steam_client.session.close()
    await steam_web_client.session.close()


app = FastAPI(lifespan=lifespan)


@app.get("/", include_in_schema=False)
async def read_root():
    response = RedirectResponse(url="/docs")
    return response


@app.get("/update", summary="Redirects to steam to update the Wardogs stats")
def update(
    state: str = Query(
        "",
        description="Token containing the discord connection",
    ),
    redirect_url: str = Query(
        "",
        description='Url to return to after the process is complete, it adds "id" and "steam_id" to the url on success, and "error" on failure',
    ),
):
    if state != "":
        state_info = jwt.decode(state, env_config.api.shared_key, algorithms="HS256")
        if (
            time.time() - state_info["created_at"]
            > env_config.api.state_lifetime_seconds
        ):
            raise HTTPException(
                status_code=403,
                detail="The given state is invalid or has expired",
            )

    callback = f"{env_config.api.auth_base_url}/callback?" + urlencode(
        {"state": state, "redirect_url": redirect_url}
    )

    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": callback,
        "openid.realm": env_config.api.auth_base_url,
        "openid.identity": ("http://specs.openid.net/auth/2.0/identifier_select"),
        "openid.claimed_id": ("http://specs.openid.net/auth/2.0/identifier_select"),
    }

    return RedirectResponse(f"{env_config.api.steam_openid}?{urlencode(params)}")


@app.get(
    "/stats", summary="Get your gathered stats via your, id, steam_id or discord_id"
)
async def stats(
    id: int | None = Query(None, description="Id of the user"),
    steam_id: int | None = Query(None, description="Steam id of the user"),
    discord_id: int | None = Query(None, description="Discord id of the user"),
) -> PlayerStats | None:
    if id is None and steam_id is None and discord_id is None:
        raise HTTPException(
            status_code=400,
            detail="You need to send the id, steam_id or discord_id of a user",
        )
    async with db.create_session() as session:
        return await stats_snapshot.get_latest(session, id, steam_id, discord_id)


@app.get(
    "/callback",
    summary="Handles the callback from steam, logs in to Wardogs and save the gathered stats to the database",
)
async def callback(
    request: Request,
    state: str = Query(
        "",
        description="Token containing the discord connection",
    ),
    redirect_url: str = Query(
        "",
        description='Url to return to after the process is complete, it adds "id" and "steam_id" to the url on success, and "error" on failure',
    ),
):
    state_info = None
    if state != "":
        state_info = jwt.decode(state, env_config.api.shared_key, algorithms="HS256")
        if (
            time.time() - state_info["created_at"]
            > env_config.api.state_lifetime_seconds
        ):
            raise HTTPException(
                status_code=403,
                detail="The given state is invalid or has expired",
            )

    required = [
        "openid.claimed_id",
        "openid.ns",
        "openid.mode",
        "openid.op_endpoint",
        "openid.identity",
        "openid.return_to",
        "openid.response_nonce",
        "openid.assoc_handle",
        "openid.signed",
        "openid.sig",
    ]

    if any(name not in request.query_params for name in required):
        return (
            "<h2>Steam returned an incomplete authentication response.</h2>",
            400,
        )

    claimed_id = request.query_params["openid.claimed_id"]

    steam_id = claimed_id.rstrip("/").split("/")[-1]

    if not steam_id.isdigit() or len(steam_id) < 16:
        return "<h2>Invalid Steam account.</h2>", 400

    provider_token = {
        "claimedId": request.query_params["openid.claimed_id"],
        "ns": request.query_params["openid.ns"],
        "mode": request.query_params["openid.mode"],
        "opEndpoint": request.query_params["openid.op_endpoint"],
        "identity": request.query_params["openid.identity"],
        "returnTo": request.query_params["openid.return_to"],
        "responseNonce": request.query_params["openid.response_nonce"],
        "assocHandle": request.query_params["openid.assoc_handle"],
        "signed": request.query_params["openid.signed"],
        "sig": request.query_params["openid.sig"],
    }

    game_token = None

    try:
        async with db.create_session() as session:
            logger.info(f"[WEB] Updating Steam account {steam_id}")

            queue_token = await steam_client.get_queue_token(env_config.api.game_host)

            game_token = await steam_client.authenticate_with_openid(
                env_config.api,
                provider_token,
                queue_token,
            )

            player_data = await steam_client.get_player_data(
                env_config.api.game_host, game_token
            )

            stats = steam_client.decode_player_stats(player_data)

            steam_user_info = await steam_web_client.get_player_summaries(
                env_config.api.steam_web_api_key, steam_id
            )

            account = await wardogs_account.get_or_create(
                session,
                steam_id=str(steam_id),
                display_name=steam_user_info.get("personaname", ""),
            )

            snapshot = await stats_snapshot.create(
                session,
                account_id=account.id,
                stats=stats,
            )

            if state_info is not None:
                await discord_user.upsert(
                    session,
                    account.id,
                    state_info["discord_id"],
                    state_info["display_name"],
                )

                async with aiohttp.ClientSession() as session:
                    await session.post(
                        url=f"{env_config.api.discord_bot_url}/notify?state_id={state_info['id']}"
                    )

                logger.info(
                    f"Discord {state_info['display_name']} linked to account {account.id}"
                )
            logger.info(f"Snapshot {snapshot.id} saved")

            if redirect_url != "":
                url_parts = list(urlparse.urlparse(redirect_url))
                query = dict(urlparse.parse_qsl(url_parts[4]))
                query.update({"id": f"{account.id}", "steam_id": steam_id})
                url_parts[4] = urlencode(query)
                return RedirectResponse(urlparse.urlunparse(url_parts))

            return RedirectResponse(
                f"{env_config.api.auth_base_url}/stats?" + urlencode({"id": account.id})
            )

    except Exception as exc:
        logger.error(f"Web update failed: {type(exc).__name__}: {exc}")

        if redirect_url != "":
            url_parts = list(urlparse.urlparse(redirect_url))
            query = dict(urlparse.parse_qsl(url_parts[4]))
            query.update({"error": "Wardogs stats update failed"})
            url_parts[4] = urlencode(query)
            return RedirectResponse(urlparse.urlunparse(url_parts))

        return {"error": "Wardogs stats update failed"}

    finally:
        game_token = None
        provider_token = None
