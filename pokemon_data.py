from typing import Any, Dict, Optional
from static_data import POKEAPI_URL

async def fetch_pokemon_full_data(client, pokemon_name: str) -> Optional[Dict[str, Any]]:
    """Get detailed Pokemon info: stats, types, first move."""
    url = f"{POKEAPI_URL}/pokemon/{pokemon_name.lower()}"
    response = await client.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    base_stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}
    types = [t["type"]["name"] for t in data["types"]]
    moves = data["moves"]
    if not moves:
        return None

    first_move_url = moves[0]["move"]["url"]
    move_resp = await client.get(first_move_url)
    if move_resp.status_code != 200:
        return None
    move_data = move_resp.json()
    move_power = move_data.get("power", 50)
    move_type = move_data.get("type", {}).get("name", "normal")
    move_name = move_data.get("name", "tackle")
    move_effect = next((e["effect"] for e in move_data.get("effect_entries", [])
                       if e["language"]["name"] == "en"), None)

    return {
        "name": data["name"],
        "base_stats": base_stats,
        "types": types,
        "move": {
            "name": move_name,
            "power": move_power,
            "type": move_type,
            "effect": move_effect,
        },
    }
