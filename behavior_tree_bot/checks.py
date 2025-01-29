

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())



# New checks for improved behaviors ! 

#NEWEST:
def have_largest_fleet(state):
    """Check if we have the largest fleet, counting ships in flight."""
    my_ships = sum(p.num_ships for p in state.my_planets()) + \
               sum(f.num_ships for f in state.my_fleets())
    enemy_ships = sum(p.num_ships for p in state.enemy_planets()) + \
                  sum(f.num_ships for f in state.enemy_fleets())
    return my_ships > enemy_ships

def need_defense(state):
    """Check if any planet needs defense based on ship count."""
    my_planets = state.my_planets()
    if not my_planets:
        return False
    weakest = min(my_planets, key=lambda p: p.num_ships)
    return weakest.num_ships < 30

def neutral_planets_available(state):
    """Check for valuable neutral planets near our territory."""
    neutral_planets = state.neutral_planets()
    my_planets = state.my_planets()
    
    if not neutral_planets or not my_planets:
        return False
        
    return any(p.growth_rate > 0 for p in neutral_planets)

def early_game_phase(state):
    """Check if we're in early game (lots of neutral planets)."""
    neutral_count = len(state.neutral_planets())
    total_planets = len(state.neutral_planets()) + len(state.enemy_planets()) + len(state.my_planets())
    return neutral_count > total_planets * 0.3

