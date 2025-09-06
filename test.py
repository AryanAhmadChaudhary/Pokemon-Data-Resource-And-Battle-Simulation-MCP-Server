import asyncio
import httpx
from battle_calculations import compute_attack_damage, process_status_hp_effect
from pokemon_data import fetch_pokemon_full_data


async def quick_checks():
    async with httpx.AsyncClient() as client:
        pikachu = await fetch_pokemon_full_data(client, "pikachu")
        bulbasaur = await fetch_pokemon_full_data(client, "bulbasaur")
        print("Pikachu data:", pikachu)
        print("Bulbasaur data:", bulbasaur)

        damage = compute_attack_damage(pikachu, bulbasaur, None)
        print(f"Pikachu does {damage} damage to Bulbasaur")

        new_hp, log = process_status_hp_effect("burn", 100)
        print(f"HP after burn: {new_hp} (log: {log})")

if __name__ == "__main__":
    asyncio.run(quick_checks())
