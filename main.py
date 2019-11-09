from log import log

player_meta_data = {
    'PLAYER_A' : {
        'name' : '',
        'mark' : '',
        'marked_location': list()
    },
    'PLAYER_B' : {
        'name' : '',
        'mark' : '',
        'marked_location': list()
    }
}

game_data = {
    "board_dimension": 3,
    "available_locations" : list(),
    "winners_cheat_sheet" : [[1,2,3], [4,5,6], [7,8,9], # vertical lines
                             [1,4,7], [2,5,8], [3,6,9], # horizontal lines
                             [1,5,9], [3,5,7]] # diagonal lines
}


# Groups the grid by 3 and loop through to print columns
def show_board():
    grouped_location = [game_data["available_locations"][k:k+game_data["board_dimension"]] \
                        for k in range(0, len(game_data["available_locations"]),\
                         game_data["board_dimension"])]
    for row in grouped_location:
        print(f"|{row[0]}|{row[1]}|{row[2]}|")

# modifying grid data and updating player data
def update_location(player, location):
    player_data = player_meta_data[player]
    game_data["available_locations"][game_data["available_locations"] \
                                    .index(location)] = player_data['mark']
    player_data['marked_location'].append(location)
    return True


# checks user marks iterating through cheat sheet
def is_winner(player_locations):
    for scenario in game_data["winners_cheat_sheet"]:
        if all(mark in player_locations for mark in scenario):
            return True
    return False

# give 2 string choices and a state outputs opposite state like, [in]on -> [out]off.
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

def get_player_location(player_name):
    show_board()
    return input(f"Where you want to place your mark, {player_name}: ")

def set_player_mark():
    choosen_mark = \
        input(f"Hello Player 1, choose your Mark ('X' or 'O'); with default as 'X': ").strip()
    if (choosen_mark != 'X' or choosen_mark != 'O'):
        choosen_mark = 'X'
    player_meta_data['PLAYER_A']['mark'] = choosen_mark
    player_meta_data['PLAYER_B']['mark'] = toggle(choosen_mark, ['X', 'O'])
    return True

def player_sign_up():
    set_player_mark()
    for idx, player in enumerate(player_meta_data.keys()):
        player_name = ''
        while len(player_name) < 1:
            player_name = input(f"I'm Player {str(idx + 1)} and My Name is: ")
        player_meta_data[player]['name'] = player_name 
    
    return True

def reset_score():
    game_data["available_locations"] = list(range(1,10))
    for player in player_meta_data.keys():
        player_meta_data[player]['marked_location'] = list()
    
    return True

def rematch_prompt(last_player):
    rematch = input(f"Another match? :")
    if rematch.lower()[0] == 'y':
        start_match(toggle(last_player, list(player_meta_data.keys())))
    log("End") # No for rematch!
    return True

def start_match(current_player='PLAYER_A'):
    log("Start")
    total_moves = 0
    reset_score()

    while True:
        print()
        location = None
        current_player_data = player_meta_data[current_player]

        # prompting for grid location until it's something that we can mark.
        while location not in game_data["available_locations"]:
            current_location = get_player_location(current_player_data['name'])
            if check_location_integrity(current_location):
                location = int(current_location)
                
        update_location(current_player, location)
            
        if is_winner(current_player_data['marked_location']):
            log("Won")
            show_board()
            rematch_prompt(current_player)
            break
        elif total_moves == 8:
            log("Tie")
            show_board()
            rematch_prompt(current_player)
            break
        else:
            total_moves += 1
            current_player = toggle(current_player, list(player_meta_data.keys()))
    
if __name__ == "__main__":
    player_sign_up()
    start_match()
