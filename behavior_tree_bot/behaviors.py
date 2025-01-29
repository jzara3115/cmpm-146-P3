import sys
from checks import early_game_phase, have_largest_fleet
sys.path.insert(0, '../')
from planet_wars import issue_order


def attack_weakest_enemy_planet_old(state):
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


def spread_to_weakest_neutral_planet_old(state):
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
def attack_weakest_enemy_planet(state):
    """Attack enemy's weakest planet with closest fleet."""
    if len(state.my_fleets()) >= 3:  # Allow more simultaneous attacks
        return False
        
    my_planets = state.my_planets()
    enemy_planets = state.enemy_planets()
    
    if not my_planets or not enemy_planets:
        return False

    # Find closest enemy planet for each of our planets
    best_attack = None
    best_distance = float('inf')
    
    for my_planet in my_planets:
        for enemy_planet in enemy_planets:
            distance = state.distance(my_planet.ID, enemy_planet.ID)
            required_ships = enemy_planet.num_ships + 1
            
            if my_planet.num_ships > required_ships * 1.1 and distance < best_distance:
                best_distance = distance
                best_attack = (my_planet, enemy_planet, required_ships)
    
    if best_attack:
        return issue_order(state, best_attack[0].ID, best_attack[1].ID, best_attack[2])
    return False

def spread_to_best_neutral_planet(state):
    """Aggressively capture neutral planets with good growth/distance ratio."""
    max_fleets = 5 if early_game_phase(state) else 3
    if len(state.my_fleets()) >= max_fleets:
        return False
        
    my_planets = state.my_planets()
    neutral_planets = state.neutral_planets()
    
    if not my_planets or not neutral_planets:
        return False

    best_value = -1
    best_attack = None
    
    for neutral_planet in neutral_planets:
        if neutral_planet.growth_rate > 0:  # Only consider growing planets
            for my_planet in my_planets:
                if my_planet.num_ships <= neutral_planet.num_ships + 1:
                    continue
                    
                distance = state.distance(my_planet.ID, neutral_planet.ID)
                # Value = growth_rate / (ships_needed * distance)
                value = neutral_planet.growth_rate / (neutral_planet.num_ships * distance + 0.1)
                
                if value > best_value:
                    best_value = value
                    best_attack = (my_planet, neutral_planet)

    if best_attack:
        return issue_order(state, best_attack[0].ID, best_attack[1].ID, 
                         best_attack[1].num_ships + 1)
    return False

def attack_high_growth_planet(state):
    """Target enemy planets with best growth/distance ratio."""
    max_fleets = 5 if have_largest_fleet(state) else 3
    if len(state.my_fleets()) >= max_fleets:
        return False
        
    my_planets = state.my_planets()
    enemy_planets = state.enemy_planets()
    
    if not my_planets or not enemy_planets:
        return False

    best_attack = None
    best_value = -1
    
    for my_planet in my_planets:
        for enemy_planet in enemy_planets:
            required_ships = enemy_planet.num_ships + 1
            if my_planet.num_ships <= required_ships * 1.1:
                continue
                
            distance = state.distance(my_planet.ID, enemy_planet.ID)
            value = enemy_planet.growth_rate / (distance + 0.1)
            
            if value > best_value:
                best_value = value
                best_attack = (my_planet, enemy_planet, required_ships)

    if best_attack:
        return issue_order(state, best_attack[0].ID, best_attack[1].ID, best_attack[2])
    return False

def defend_weak_planet(state):
    """Defend weak planets from closest strong planet."""
    if len(state.my_fleets()) >= 6:
        return False

    my_planets = state.my_planets()
    if not my_planets:
        return False

    def strength(p):
        return p.num_ships + sum(fleet.num_ships for fleet in state.my_fleets() if fleet.destination_planet == p.ID) - sum(fleet.num_ships for fleet in state.enemy_fleets() if fleet.destination_planet == p.ID)

    avg = sum(strength(planet) for planet in my_planets) / len(my_planets)

    weak_planets = [planet for planet in my_planets if strength(planet) < avg]
    strong_planets = [planet for planet in my_planets if strength(planet) > avg]

    if not weak_planets or not strong_planets:
        return False

    weak_planets = iter(sorted(weak_planets, key=strength))
    strong_planets = iter(sorted(strong_planets, key=strength, reverse=True))

    try:
        weak_planet = next(weak_planets)
        strong_planet = next(strong_planets)
        while True:
            need = int(avg - strength(weak_planet))
            have = int(strength(strong_planet) - avg)

            if have >= need > 0:
                issue_order(state, strong_planet.ID, weak_planet.ID, need)
                weak_planet = next(weak_planets)
                strong_planet = next(strong_planets)
            elif have > 0:
                issue_order(state, strong_planet.ID, weak_planet.ID, have)
                strong_planet = next(strong_planets)
            else:
                weak_planet = next(weak_planets)

    except StopIteration:
        return False
