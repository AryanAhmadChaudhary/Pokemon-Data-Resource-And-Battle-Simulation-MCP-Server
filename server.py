import httpx
import random
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from static_data import STATUS_PARALYSIS, POKEAPI_URL
from battle_calculations import (compute_attack_damage, process_status_hp_effect, try_infest_status, extract_evolution_names)
from pokemon_data import fetch_pokemon_full_data

mcp = FastMCP("pokemon")

@mcp.tool()
async def retrieve_pokemon_info(pokemon_name: str) -> Dict[str, Any]:
    """Expose detailed info about a Pokemon"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{POKEAPI_URL}/pokemon/{pokemon_name.lower()}"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            stats = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}
            types = [t["type"]["name"] for t in data["types"]]

            abilities = []
            for ability_info in data["abilities"]:
                ab_name = ability_info["ability"]["name"]
                ab_url = ability_info["ability"]["url"]
                ab_response = await client.get(ab_url)
                ab_response.raise_for_status()
                ab_data = ab_response.json()
                desc = next((entry["effect"] for entry in ab_data.get("effect_entries", [])
                            if entry["language"]["name"] == "en"), None)
                abilities.append({"name": ab_name, "effect": desc})

            moves = []
            for mv in data["moves"][:10]:
                mv_name = mv["move"]["name"]
                mv_url = mv["move"]["url"]
                mv_response = await client.get(mv_url)
                mv_response.raise_for_status()
                mv_data = mv_response.json()
                effect = next((entry["effect"] for entry in mv_data.get("effect_entries", [])
                              if entry["language"]["name"] == "en"), None)
                moves.append({"name": mv_name, "effect": effect})

            species_url = data["species"]["url"]
            sp_response = await client.get(species_url)
            sp_response.raise_for_status()
            sp_data = sp_response.json()
            evo_chain_url = sp_data["evolution_chain"]["url"]
            evo_response = await client.get(evo_chain_url)
            evo_response.raise_for_status()
            evo_data = evo_response.json()
            evo_chain = extract_evolution_names(evo_data["chain"])

            return {
                "name": data["name"],
                "id": data["id"],
                "base_stats": stats,
                "types": types,
                "abilities": abilities,
                "moves": moves,
                "evolution_chain": evo_chain,
            }
    except httpx.HTTPStatusError as e:
        return {"error": f"Status error: {e}"}
    except httpx.RequestError as e:
        return {"error": f"Connection error: {e}"}

@mcp.tool()
async def simulate_battle(pokemon_one: str, pokemon_two: str) -> Dict[str, Any]:
    """Simulate a turn-based Pokemon battle with types and status effects."""
    async with httpx.AsyncClient() as client:
        p1 = await fetch_pokemon_full_data(client, pokemon_one)
        if not p1:
            return {"error": f"Data not found for {pokemon_one}."}
        p2 = await fetch_pokemon_full_data(client, pokemon_two)
        if not p2:
            return {"error": f"Data not found for {pokemon_two}."}

        hp1 = p1["base_stats"].get("hp", 100)
        hp2 = p2["base_stats"].get("hp", 100)
        status1 = None
        status2 = None
        log = []
        round_counter = 1

        speed1 = p1["base_stats"].get("speed", 50)
        speed2 = p2["base_stats"].get("speed", 50)

        first, second = (p1, p2) if speed1 >= speed2 else (p2, p1)
        first_hp, second_hp = (hp1, hp2) if speed1 >= speed2 else (hp2, hp1)
        first_status, second_status = status1, status2
        first_name, second_name = first["name"], second["name"]

        while first_hp > 0 and second_hp > 0:
            log.append(f"Round {round_counter}:")

            # First attacks
            if first_status == STATUS_PARALYSIS and random.random() < 0.25:
                log.append(f"{first_name} is paralyzed and can't move!")
            else:
                dmg = compute_attack_damage(first, second, first_status)
                second_hp -= dmg
                log.append(f"{first_name} used {first['move']['name']} causing {dmg} damage! ({second_name} HP: {max(0, second_hp)})")
                new_status = try_infest_status(first["move"])
                if not second_status and new_status:
                    second_status = new_status
                    log.append(f"{second_name} got {new_status}!")
                second_hp, status_log = process_status_hp_effect(second_status, second_hp)
                if status_log:
                    log.append(f"{second_name}: {status_log} (HP: {max(0, second_hp)})")
                if second_hp <= 0:
                    log.append(f"{second_name} fainted!")
                    break

            # Second attacks
            if second_hp > 0:
                if second_status == STATUS_PARALYSIS and random.random() < 0.25:
                    log.append(f"{second_name} is paralyzed and can't move!")
                else:
                    dmg = compute_attack_damage(second, first, second_status)
                    first_hp -= dmg
                    log.append(f"{second_name} used {second['move']['name']} causing {dmg} damage! ({first_name} HP: {max(0, first_hp)})")
                    new_status = try_infest_status(second["move"])
                    if not first_status and new_status:
                        first_status = new_status
                        log.append(f"{first_name} got {new_status}!")
                    first_hp, status_log = process_status_hp_effect(first_status, first_hp)
                    if status_log:
                        log.append(f"{first_name}: {status_log} (HP: {max(0, first_hp)})")
                    if first_hp <= 0:
                        log.append(f"{first_name} fainted!")
                        break

            round_counter += 1

        winner = first_name if first_hp > 0 else second_name
        log.append(f"Winner: {winner}!")

        return {
            "pokemon_1": p1["name"],
            "pokemon_2": p2["name"],
            "initial_hp": {p1["name"]: hp1, p2["name"]: hp2},
            "battle_log": log,
            "winner": winner,
        }

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8080)
