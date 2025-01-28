

def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())



# New checks for improved behaviors ! 
def have_more_growth_rate(state):
    """Check if we have higher ship production than enemy."""
    my_growth = sum(p.growth_rate for p in state.my_planets())
    enemy_growth = sum(p.growth_rate for p in state.enemy_planets())
    return my_growth > enemy_growth

def under_attack(state):
    """Check if any of our planets are under attack."""
    return any(f.destination_planet in [p.ID for p in state.my_planets()] 
              for f in state.enemy_fleets())

def neutral_planets_available(state):
    """Check if there are neutral planets worth capturing."""
    return any(p.growth_rate > 0 for p in state.neutral_planets())

def enemy_planets_available(state):
    """Check if there are enemy planets to attack."""
    return len(state.enemy_planets()) > 0

