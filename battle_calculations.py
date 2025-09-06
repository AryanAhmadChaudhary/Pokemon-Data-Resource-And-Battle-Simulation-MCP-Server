import random
from typing import Any, Dict, List, Optional, Tuple
from static_data import (attack_effects,STATUS_PARALYSIS,STATUS_BURN,STATUS_POISON)

def try_infest_status(move: Dict[str, Any]) -> Optional[str]:
    """Determine if a status effect is inflicted by the move."""
    effect = (move.get("effect") or "").lower()
    if "paralyze" in effect:
        return STATUS_PARALYSIS if random.random() < 0.2 else None
    if "burn" in effect:
        return STATUS_BURN if random.random() < 0.2 else None
    if "poison" in effect:
        return STATUS_POISON if random.random() < 0.2 else None
    return None

def compute_attack_damage(attacker: Dict[str, Any], defender: Dict[str, Any], status: Optional[str]) -> int:
    """Calculate damage inflicted by attacker on defender considering status effects."""
    move = attacker["move"]
    attack_stat = attacker["base_stats"].get("attack", 50)
    defense_stat = defender["base_stats"].get("defense", 50)
    power = move.get("power") or 50

    # Halve attack if attacker is burned
    if status == STATUS_BURN:
        attack_stat = attack_stat // 2

    type_multiplier = compute_type_effectiveness(move["type"], defender["types"])

    damage = int((((2 * 50 / 5 + 2) * power * attack_stat / defense_stat) / 50 + 2) * type_multiplier)
    return max(1, damage)

def extract_evolution_names(chain) -> List[str]:
    """Traverse the evolution chain dict to get Pokémon names in sequence."""
    evo_names = []
    current = chain
    while current:
        evo_names.append(current["species"]["name"])
        current = current["evolves_to"][0] if current["evolves_to"] else None
    return evo_names

def compute_type_effectiveness(attack_type: str, defender_types: List[str]) -> float:
    """Calculate damage multiplier based on attacker and defender types."""
    multiplier = 1.0
    for d_type in defender_types:
        multiplier *= attack_effects.get(attack_type, {}).get(d_type, 1.0)
    return multiplier


def process_status_hp_effect(status: Optional[str], hp: int) -> Tuple[int, str]:
    """Apply damage from a status condition and return updated HP and effect description."""
    log = ""
    if status == STATUS_BURN:
        burn_damage = max(1, hp // 16)
        hp -= burn_damage
        log = f"Burn caused {burn_damage} damage. "
    elif status == STATUS_POISON:
        poison_damage = max(1, hp // 8)
        hp -= poison_damage
        log = f"Poison caused {poison_damage} damage. "
    return hp, log
