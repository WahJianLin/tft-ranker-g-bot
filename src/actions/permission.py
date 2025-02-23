from typing import List

from discord import Role

ROLE_MODS = 'mods'

def is_mod(roles: List[Role]) -> bool:
    return any(role.name.lower() == ROLE_MODS for role in roles)
