from log import log
from config import player_meta_data, game_data
from machine import machine_move, boot_machine
from helper import flip
import redis
import json

redis_client = redis.Redis(host='0.0.0.0', port=7001, db=0)

def publish_data(key, value):
    try:
        redis_client.publish(key, value)
        redis_client.set(key, value)
    except e:
        print(e)
    return

# modifying grid data and updating player data
def update_location(player, location):
    print(player, location)
    player_data = player_meta_data[player]
    game_data["available_locations"][game_data["available_locations"] \
                                    .index(location)] = player_data['mark']
    player_data['marked_location'].append(location)
    publish_data('available_grid', json.dumps(game_data["available_locations"]))
    return True


# checks user marks iterating through cheat sheet
def is_winner(player_locations):
    for scenario in game_data["winners_cheat_sheet"]:
        if all(mark in player_locations for mark in scenario):
            return True
    return False

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

def get_player_location(player_id, mark):
    publish_data('current_player', player_id)
    pubsub = redis_client.pubsub()
    pubsub.subscribe(['move'])
    for move in pubsub.listen():
        if move['type'] == 'message':
            pubsub.unsubscribe()
            return json.loads(move['data'])['move']

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
        roll_game(flip(last_player, list(player_meta_data.keys())))
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
        current_player = flip(current_player, list(player_meta_data.keys()))
        return roll_game(current_player)

def roll_game(current_player):
    # print()
    location = None
    current_player_data = player_meta_data[current_player]

    # prompting for grid location until it's something that we can mark.
    if current_player == 'MACHINE' and game_data["machine_mode"]:
        location = machine_move()
    else:
        while location not in game_data["available_locations"]:
            current_location = get_player_location(current_player, current_player_data['mark'])
            if check_location_integrity(current_location):
                location = int(current_location)
                
    update_location(current_player, location)
    return analyze_match(current_player_data, current_player)

def update_player(user_data):
    if len(player_meta_data) > 1:
        return False
    player_id = user_data["id"]
    player_meta_data[player_id] = {}
    player_meta_data[player_id]['name'] = user_data['name']
    player_meta_data[player_id]['mark'] = game_data["available_marks"][len(player_meta_data) - 1]
    player_meta_data[player_id]['marked_location'] = []
    game_data["user_signed_up"] += 1
    return player_meta_data

def initate_shared_objects():
    publish_data('match_state', 1)
    publish_data('available_grid', json.dumps(game_data['available_locations']))
    return

def register_users():
    pubsub = redis_client.pubsub()
    pubsub.subscribe(['register_user', 'machine_mode'])
    for user in pubsub.listen():
        channel = user['channel'].decode('ascii')
        if (user['type'] == 'message' and channel == 'machine_mode'):
            if user['data'].decode('ascii') == 'True':
                game_data["user_registered"] += 1
                update_player({"name": "Mr. 🤖", "id" : "MACHINE"})
                print('machine mode enabled')
                boot_machine()
                print(game_data)
        if (user['type'] == 'message' and channel == 'register_user'):
            game_data["user_registered"] += 1
            
        if game_data["user_registered"] == game_data["player_limit"]:
            pubsub.unsubscribe()
    return

def is_user_registered(pubsub):
    if game_data["user_signed_up"] == game_data["player_limit"]:
        return pubsub.unsubscribe()
    return False

def listen_user_details():
    pubsub = redis_client.pubsub()
    pubsub.subscribe(['user_info'])
    for user in pubsub.listen():
        if user['type'] == 'message':
            update_player(json.loads(user['data']))
        is_user_registered(pubsub)
    return

if __name__ == "__main__":
    print("waiting for players to sign-up")
    register_users()
    initate_shared_objects()
    listen_user_details()
    roll_game(list(player_meta_data.keys())[0])
