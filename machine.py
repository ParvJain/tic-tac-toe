import copy
import random
from config import game_data, player_meta_data


def boot_machine():
    game_data["machine_mode"] = True
    return True

def get_available_slots():
    return [col for col in game_data["available_locations"] if type(col) is int]

def gather_data(next_move_arr):
    rank = dict()
    possible_move = next_move_arr[-1]
    for cheat in game_data["winners_cheat_sheet"]:
        level = len(set(next_move_arr) & set(cheat))
        if level not in rank:
            rank[level] = []
        if possible_move not in rank[level]:
            rank[level].append(possible_move)
    return rank

def analyze_move(ranked_map):
    # to win, or not opponent win.
    power_move = 3
    if power_move in ranked_map["attack"]:
        return ranked_map["attack"][power_move][0]
    if power_move in ranked_map["defend"]:
        return ranked_map["defend"][power_move][0]

    # traverse through 2 -> 1 -> 0 to find best possible, yet random move.
    for level in range(2,-1,-1):
        if level in ranked_map["attack"].keys() or level in ranked_map["defend"]:
            possible_attack_moves = ranked_map["attack"][level] \
                                        if level in ranked_map["attack"] else []
            possible_defense_moves = ranked_map["defend"][level] \
                                        if level in ranked_map["defend"] else []
            combined_moves_set = list(set(possible_attack_moves) & set(possible_defense_moves))
            if len(combined_moves_set) == 0:
                duck_move = list(set(possible_attack_moves + possible_defense_moves))
                return random.choice(duck_move)
            return random.choice(combined_moves_set)
    return True

def machine_move():
    available_moves = get_available_slots()
    rank = dict(attack={}, defend={})
    machine_historical_data = player_meta_data["PLAYER_A"]["marked_location"]
    opponent_historical_data = player_meta_data["PLAYER_B"]["marked_location"]

    for move in available_moves:
        machine_next_move = copy.deepcopy(machine_historical_data)
        machine_next_move.append(move)
        move_data = gather_data(machine_next_move)
        for level in move_data.keys():
            if level not in rank["attack"]:
                rank["attack"][level] = []
            rank["attack"][level] = list(set(rank["attack"][level]+ move_data[level]))
        opponent_next_move = copy.deepcopy(opponent_historical_data)
        opponent_next_move.append(move)
        move_data = gather_data(opponent_next_move)
        for level in move_data.keys():
            if level not in rank["defend"]:
                rank["defend"][level] = []
            rank["defend"][level] = list(set(rank["defend"][level]+ move_data[level]))

    return analyze_move(rank)
