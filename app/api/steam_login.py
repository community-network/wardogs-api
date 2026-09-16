import base64
import json

import requests
from main import env_config

from app.api.wardogs_models import PlayerStats, RoleStats, UnlockInfo


def get_queue_token():
    response = requests.post(
        f"{env_config.api.game_host}/v1/loginqueue/getinqueuev1",
        json={},
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    token = (
        data.get("loginQueuePassToken") or data.get("passToken") or data.get("token")
    )

    if not token:
        raise RuntimeError("WARDOGS returned no login queue token.")

    return token


def authenticate_with_openid(
    provider_token,
    queue_token,
):
    payload = {
        "providerId": "STEAM",
        "providerToken": json.dumps(
            provider_token,
            separators=(",", ":"),
        ),
        "gameShardId": env_config.api.game_shard_id,
        "loginQueuePassToken": queue_token,
    }

    # Keep this request identical to the version
    # proven to work in steam_web_test.py.
    response = requests.post(
        (f"{env_config.api.social_host}/v1/account/authenticateorcreatev2"),
        json=payload,
        timeout=30,
    )

    if not response.ok:
        raise RuntimeError(
            f"WARDOGS authentication failed (HTTP {response.status_code})."
        )

    data = response.json()

    tokens = data.get("pragmaTokens")

    if not isinstance(tokens, dict):
        raise RuntimeError("WARDOGS returned invalid token data.")

    game_token = tokens.get("pragmaGameToken")

    if not game_token:
        raise RuntimeError("WARDOGS returned no game session.")

    return game_token


def get_player_data(game_token):
    payload = {
        "requestId": 1,
        "type": "PlayerDataServiceRpc.GetV1Request",
        "payload": {},
    }

    response = requests.post(
        f"{env_config.api.game_host}/v1/rpc",
        json=payload,
        headers={
            "Authorization": f"Bearer {game_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    if not response.ok:
        raise RuntimeError(
            f"WARDOGS PlayerData request failed (HTTP {response.status_code})."
        )

    return response.json()


def decode_player_stats(data):
    rpc_response = data.get("response", {})
    payload = rpc_response.get("payload", {})
    player_data = payload.get("playerData", {})

    if not isinstance(player_data, dict):
        raise RuntimeError("WARDOGS returned invalid PlayerData.")

    raw_version = player_data.get("version")

    stats = PlayerStats(
        player_data_version=(int(raw_version) if raw_version is not None else None)
    )

    entities = player_data.get("entities", [])

    if not isinstance(entities, list):
        raise RuntimeError("WARDOGS returned invalid entity data.")

    role_map = {
        "Infantry": "infantry",
        "Medic": "medic",
        "Recon": "recon",
        "Support": "support",
        "Driver": "driver",
        "Pilot": "pilot",
    }

    for entity in entities:
        components = entity.get("components")

        if components is None:
            components = [entity]

        if isinstance(components, dict):
            components = [components]

        if not isinstance(components, list):
            continue

        for component in components:
            serialized = component.get(
                "serializedComponent",
                {},
            )

            encoded = serialized.get("bytes")

            if not encoded:
                continue

            try:
                decoded = base64.b64decode(encoded).decode("utf-8")

                obj = json.loads(decoded)

            except Exception:
                continue

            if not isinstance(obj, dict):
                continue

            node_id = obj.get("nodeId")

            if node_id:
                try:
                    level = int(obj.get("level", 1))
                except (TypeError, ValueError):
                    level = 1

                stats.unlocks.append(
                    UnlockInfo(
                        node_id=str(node_id),
                        level=level,
                    )
                )

            attribute_id = obj.get("id")

            if attribute_id == "Attribute.Meta.Currency.Cash":
                stats.cash = int(obj.get("amount", 0))

            elif attribute_id == "Attribute.Meta.Currency.GoldBars":
                stats.gold = int(obj.get("amount", 0))

            xp_id = obj.get("xpId")

            if not xp_id:
                continue

            prefix = "Attribute.Meta.XP.Role."

            if not xp_id.startswith(prefix):
                continue

            role_name = xp_id[len(prefix) :]
            attribute_name = role_map.get(role_name)

            if not attribute_name:
                continue

            setattr(
                stats,
                attribute_name,
                RoleStats(
                    level=int(obj.get("rewardedLevel", 0)),
                    xp=int(obj.get("amount", 0)),
                ),
            )

    return stats
