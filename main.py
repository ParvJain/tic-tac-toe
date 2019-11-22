from log import log
from config import player_meta_data, game_data
from machine import machine_move, boot_machine
import redis
import json

redis_client = redis.Redis(host='0.0.0.0', port=7001, db=0)

# modifying grid data and updating player data
def update_location(player, location):
    print(player, location)
    player_data = player_meta_data[player]
    game_data["available_locations"][game_data["available_locations"] \
                                    .index(location)] = player_data['mark']
    player_data['marked_location'].append(location)
    redis_client.publish('available_grid', json.dumps(game_data["available_locations"]))
    return True


# checks user marks iterating through cheat sheet
def is_winner(player_locations):
    for scenario in game_data["winners_cheat_sheet"]:
        if all(mark in player_locations for mark in scenario):
            return True
    return False

# give 2 string choices and a state; outputs opposite state like, [in]on -> [out]off.
def toggle(state, choices):
    if len(choices) < 1:
        log("MethodNotSupported")
        return 
    state = str(state).strip()
    if state not in choices:
        log("InvalidChoice")
    choices.remove(state)
    return choices[0]

def is_location_taken(new_location):
    return int(new_location) not in game_data["available_locations"]

# checks location type and availability
def check_location_integrity(new_location):
    if not new_location.isdecimal():
        log("NaN")
        return False
    elif is_location_taken(int(new_location)):
        log("OutOfRange")
        return False
    return True

def mark_parser(choice):
    if choice.lower() == 'x':
        return 'X'
    elif choice.lower() == 'o':
        return 'O'
    return 'X'

def get_player_location(player_name, mark):
    redis_client.publish('current_player', player_name)
    pubsub = redis_client.pubsub()
    pubsub.subscribe(['move'])
    for move in pubsub.listen():
        if move['type'] == 'message':
            pubsub.unsubscribe()
            return json.loads(move['data'])['move']

def set_player_mark(choosen_mark):
    sanitized_mark = mark_parser(choosen_mark)
    reversed_sanitized_mark = toggle(sanitized_mark, ['X', 'O'])
    print(f"Player 1 will play as '{sanitized_mark}', and Player 2 '{reversed_sanitized_mark}'")
    player_meta_data['PLAYER_A']['mark'] = sanitized_mark
    player_meta_data['PLAYER_B']['mark'] = reversed_sanitized_mark
    return True

def reset_score():
    game_data["available_locations"] = list(range(1,10))
    for player in player_meta_data.keys():
        player_meta_data[player]['marked_location'] = list()
    game_data["total_moves"] = 0
    return True

def show_score():
    count = lambda name: game_data["historical_score_data"].count(name)
    print()
    print("SCOREBOARD!")
    print(f"{player_meta_data['PLAYER_A']['name']} - {count('PLAYER_A')}")
    print(f"{player_meta_data['PLAYER_B']['name']} - {count('PLAYER_B')}")
    print(f"Tie - {count('TIE')}")

def rematch_prompt(last_player):
    rematch = input(f"Another match? (yes, no) : ")
    show_score()
    if rematch.lower()[0] == 'y':
        reset_score()
        roll_game(toggle(last_player, list(player_meta_data.keys())))
    else:
        log("End") # No for rematch!
    return True

def analyze_match(current_player_data, current_player):
    if is_winner(current_player_data['marked_location']):
        print(f"{current_player_data['name']} Won! 🎉")
        log("Won")
        # show_board()
        game_data["historical_score_data"].append(current_player)
        return rematch_prompt(current_player)
    elif game_data["total_moves"] == 8:
        log("Tie")
        # show_board()
        game_data["historical_score_data"].append('TIE')
        return rematch_prompt(current_player)
    else:
        game_data["total_moves"] += 1
        current_player = toggle(current_player, list(player_meta_data.keys()))
        return roll_game(current_player)

def roll_game(current_player='PLAYER_A'):
    # print()
    location = None
    current_player_data = player_meta_data[current_player]

    # prompting for grid location until it's something that we can mark.
    if current_player == 'PLAYER_A' and game_data["machine_mode"]:
        location = machine_move()
    else:
        while location not in game_data["available_locations"]:
            current_location = get_player_location(current_player_data['name'], \
                                                    current_player_data['mark'])
            if check_location_integrity(current_location):
                location = int(current_location)
                
    update_location(current_player, location)
    return analyze_match(current_player_data, current_player)

def update_user_state():
    pass

def update_player(user_data):
    if len(player_meta_data) > 1:
        return False
    current_player = 'PLAYER_A' if len(player_meta_data) == 0 else 'PLAYER_B'
    player_mark = {"PLAYER_A": "X", "PLAYER_B": "O"}
    player_meta_data[current_player] = {}
    player_meta_data[current_player]['name'] = user_data['name']
    player_meta_data[current_player]['mark'] = player_mark[current_player]
    player_meta_data[current_player]['marked_location'] = []
    return player_meta_data

def initate_shared_objects():
    redis_client.publish('match_state', 1)
    redis_client.publish('available_grid', json.dumps(game_data['available_locations']))
    redis_client.publish('match_decision', '')
    redis_client.publish('current_player', '')
    redis_client.publish('move', '')
    return

users = []
def register_users():
    pubsub = redis_client.pubsub()
    pubsub.subscribe(['register_user', 'machine_mode'])
    for user in pubsub.listen():
        channel = user['channel'].decode('ascii')
        if (user['type'] == 'message' and channel == 'register_user'):
            users.append(user['data'])
        if (user['type'] == 'message' and channel == 'machine_mode'):
            if user['data'].decode('ascii') == 'True':
                users.append('MACHINE')
                update_player({"name": "Mr. 🤖"})
                print('machine mode enabled')
                boot_machine()
        if len(users) == 2:
            pubsub.unsubscribe()
    return

def is_user_registered(pubsub):
    if len(users) == 0:
        return pubsub.unsubscribe()
    if game_data['machine_mode']:
        users.pop(0)
    return False

def listen_user_details():
    pubsub = redis_client.pubsub()
    pubsub.subscribe(['user_info'])
    for user in pubsub.listen():
        if user['type'] == 'message':
            update_player(json.loads(user['data']))
            users.pop(0)
        is_user_registered(pubsub)
    return
    
    
if __name__ == "__main__":
    print("waiting for players to sign-up")
    register_users()
    initate_shared_objects()
    listen_user_details()
    roll_game()
