from urllib.parse import urlencode

from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse

from app.api.steam_login import (
    authenticate_with_openid,
    decode_player_stats,
    get_player_data,
    get_queue_token,
)
from config import load_config

app = FastAPI()

env_config = load_config()


@app.get("/login")
def login(
    state: str | None = Query(
        None,
        description="Name of the server you want to search for",
        examples=["BoB"],
    ),
):
    state = request.args.get("state", "")

    pending = _get_pending_state(state)

    if pending is None:
        return (
            "<h2>This WARDOGS update link is invalid or has expired.</h2>",
            400,
        )

    callback = f"{env_config.api.auth_base_url}/callback?" + urlencode({"state": state})

    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": callback,
        "openid.realm": env_config.api.auth_base_url,
        "openid.identity": ("http://specs.openid.net/auth/2.0/identifier_select"),
        "openid.claimed_id": ("http://specs.openid.net/auth/2.0/identifier_select"),
    }

    return RedirectResponse(f"{env_config.api.steam_openid}?{urlencode(params)}")


@app.get("/callback")
def callback():
    state = request.args.get("state", "")

    pending = _get_pending_state(state)

    if pending is None:
        return (
            "<h2>This WARDOGS update request is invalid or has expired.</h2>",
            400,
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

    if any(name not in request.args for name in required):
        return (
            "<h2>Steam returned an incomplete authentication response.</h2>",
            400,
        )

    claimed_id = request.args["openid.claimed_id"]

    steam_id = claimed_id.rstrip("/").split("/")[-1]

    if not steam_id.isdigit() or len(steam_id) < 16:
        return "<h2>Invalid Steam account.</h2>", 400

    provider_token = {
        "claimedId": request.args["openid.claimed_id"],
        "ns": request.args["openid.ns"],
        "mode": request.args["openid.mode"],
        "opEndpoint": request.args["openid.op_endpoint"],
        "identity": request.args["openid.identity"],
        "returnTo": request.args["openid.return_to"],
        "responseNonce": request.args["openid.response_nonce"],
        "assocHandle": request.args["openid.assoc_handle"],
        "signed": request.args["openid.signed"],
        "sig": request.args["openid.sig"],
    }

    game_token = None

    try:
        print()
        print(f"[WEB] Updating Steam account {steam_id}")

        queue_token = get_queue_token()

        game_token = authenticate_with_openid(
            provider_token,
            queue_token,
        )

        player_data = get_player_data(game_token)

        stats = decode_player_stats(player_data)

        account_id = get_or_create_account(steam_id=str(steam_id))

        snapshot_id = save_snapshot(
            account_id=account_id,
            stats=stats,
        )

        # Link only after WARDOGS authentication
        # and PlayerData retrieval succeeded.
        link_discord_user(
            discord_id=pending["discord_id"],
            account_id=account_id,
        )

        # Successful requests are single-use.
        _consume_pending_state(state)

        print(f"[OK] Discord {pending['discord_id']} linked to account {account_id}")
        print(f"[OK] Snapshot {snapshot_id} saved")

        return f"""
        <!doctype html>
        <html>
        <head>
            <title>WARDOGS Stats Updated</title>
        </head>
        <body>
            <h2>WARDOGS stats updated successfully</h2>

            <p>
                Wardog Level:
                <strong>{stats.wardog_level}</strong>
            </p>

            <p>
                Cash:
                <strong>{stats.cash:,}</strong>
            </p>

            <p>
                Unlocks:
                <strong>{len(stats.unlocks)}</strong>
            </p>

            <p>
                Your WARDOGS account is now linked
                to your Discord account.
            </p>

            <p>
                You can close this page and return
                to Discord.
            </p>
        </body>
        </html>
        """

    except Exception as exc:
        print(f"[ERROR] Web update failed: {type(exc).__name__}: {exc}")

        return (
            """
        <!doctype html>
        <html>
        <head>
            <title>WARDOGS Update Failed</title>
        </head>
        <body>
            <h2>WARDOGS stats update failed</h2>

            <p>
                No account changes were made.
                Return to Discord and try again.
            </p>
        </body>
        </html>
        """,
            500,
        )

    finally:
        game_token = None
        provider_token = None
