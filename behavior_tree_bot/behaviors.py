import sys
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet(state):
    # (1) If we currently have a fleet in flight, abort plan.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)

    # (3) Find the weakest enemy planet.
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)


# New behavior functions:
# New implementation for behaviors.py
def attack_weakest_enemy_planet_aggressive(state):
    """Attack with more ships to ensure conquest."""
    strongest_planet = max(state.my_planets(), key=lambda t: t.num_ships, default=None)
    weakest_planet = min(state.enemy_planets(), key=lambda t: t.num_ships, default=None)
    
    if not strongest_planet or not weakest_planet:
        return False
        
    required_ships = weakest_planet.num_ships + 1
    if strongest_planet.num_ships > required_ships:
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, required_ships)
    return False

def attack_highest_growth_enemy_planet(state):
    """Target enemy planets with highest ship production."""
    my_planets = state.my_planets()
    if len(my_planets) == 0:
        return False
        
    strongest_planet = max(my_planets, key=lambda p: p.num_ships)
    
    enemy_planets = [(p, p.growth_rate) for p in state.enemy_planets()]
    if not enemy_planets:
        return False
        
    target_planet = max(enemy_planets, key=lambda p: p[1])[0]
    required_ships = target_planet.num_ships + 1
    
    if strongest_planet.num_ships > required_ships:
        return issue_order(state, strongest_planet.ID, target_planet.ID, required_ships)
    return False

def spread_to_best_growth_neutral(state):
    """Target neutral planets with best growth/cost ratio."""
    if len(state.my_fleets()) >= 3:  # Limit concurrent expansions
        return False
        
    my_planets = [p for p in state.my_planets()]
    if not my_planets:
        return False
        
    neutral_planets = [(p, p.growth_rate / (p.num_ships + 0.1)) for p in state.neutral_planets()]
    if not neutral_planets:
        return False
        
    target_planet = max(neutral_planets, key=lambda p: p[1])[0]
    strongest_planet = max(my_planets, key=lambda p: p.num_ships)
    
    if strongest_planet.num_ships > target_planet.num_ships + 1:
        return issue_order(state, strongest_planet.ID, target_planet.ID, target_planet.num_ships + 1)
    return False

def defend_weakest_planet(state):
    """Reinforce planets under threat."""
    my_planets = [p for p in state.my_planets()]
    if len(my_planets) <= 1:
        return False
        
    # Find planets under threat
    weakest_planet = min(my_planets, key=lambda p: p.num_ships)
    
    # Check if there are enemy fleets targeting this planet
    enemy_fleets = [f for f in state.enemy_fleets() if f.destination_planet == weakest_planet.ID]
    if not enemy_fleets:
        return False
        
    # Calculate total incoming attack
    total_attack = sum(f.num_ships for f in enemy_fleets)
    
    # Find reinforcement source
    other_planets = [p for p in my_planets if p.ID != weakest_planet.ID]
    if not other_planets:
        return False
        
    strongest_planet = max(other_planets, key=lambda p: p.num_ships)
    
    # Send reinforcements if we can help
    ships_needed = total_attack + 1 - weakest_planet.num_ships
    if strongest_planet.num_ships > ships_needed:
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, ships_needed)
    return False

