#!/usr/bin/env python
#

"""
// There is already a basic strategy in place here. You can use it as a
// starting point, or you can throw it out entirely and replace it with your
// own.
"""
import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check

from planet_wars import PlanetWars, finish_turn


# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots

# New behavior tree for our bot using new functions in bt_bot.py
def setup_behavior_tree():
    """Set up the behavior tree for the bot."""
    root = Selector(name='Root')
    
    # Early game expansion
    early_expansion = Sequence(name='Early Game Expansion')
    early_game_check = Check(early_game_phase)
    neutral_expansion = Action(spread_to_best_neutral_planet)
    early_expansion.child_nodes = [early_game_check, neutral_expansion]
    
    # Defensive plan
    defensive_plan = Sequence(name='Defensive Strategy')
    defense_check = Check(need_defense)
    defend_action = Action(defend_weak_planet)
    defensive_plan.child_nodes = [defense_check, defend_action]
    
    # Aggressive plan
    aggressive_plan = Sequence(name='Aggressive Strategy')
    fleet_check = Check(have_largest_fleet)
    attack_action = Action(attack_high_growth_planet)
    aggressive_plan.child_nodes = [fleet_check, attack_action]
    
    # Fallback plan
    fallback_plan = Sequence(name='Fallback Strategy')
    fallback_action = Action(defend_weak_planet)
    fallback_attack = Action(attack_weakest_enemy_planet)
    
    root.child_nodes = [early_expansion, aggressive_plan, defensive_plan, fallback_plan]
    
    return root


# You don't need to change this function
def do_turn(state):
    behavior_tree.execute(planet_wars)

if __name__ == '__main__':
    logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

    behavior_tree = setup_behavior_tree()
    try:
        map_data = ''
        while True:
            current_line = input()
            if len(current_line) >= 2 and current_line.startswith("go"):
                planet_wars = PlanetWars(map_data)
                do_turn(planet_wars)
                finish_turn()
                map_data = ''
            else:
                map_data += current_line + '\n'

    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
    except Exception:
        traceback.print_exc(file=sys.stdout)
        logging.exception("Error in bot.")





