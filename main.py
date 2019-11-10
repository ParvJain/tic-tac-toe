from log import log
from config import player_meta_data, game_data
from machine import machine_move, boot_machine

def magic_cols(row):
    fg = lambda text, color: "\33[38;5;" + str(color) + "m" + text + "\33[0m"
    column_list = list()
    for col in row:
        if type(col) is int:
            column_list.append(fg(str(col), 11))
        elif (col == 'X'):
            column_list.append(fg(col, 21))
        elif (col == 'O'):
            column_list.append(fg(col, 9))
    return column_list

# Groups the grid by 3 and loop through to print columns
def show_board():
    grouped_location = [game_data["available_locations"][k:k+game_data["board_dimension"]] \
                        for k in range(0, len(game_data["available_locations"]),\
                         game_data["board_dimension"])]
    for row in grouped_location:
        row = magic_cols(row)
        print(f"|{row[0]}|{row[1]}|{row[2]}|")
    return True

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
    show_board()
    return input(f"It's your turn 🎲, {player_name} you're {mark} : ")

def set_player_mark(choosen_mark):
    sanitized_mark = mark_parser(choosen_mark)
    reversed_sanitized_mark = toggle(sanitized_mark, ['X', 'O'])
    print(f"Player 1 will play as '{sanitized_mark}', and Player 2 '{reversed_sanitized_mark}'")
    player_meta_data['PLAYER_A']['mark'] = sanitized_mark
    player_meta_data['PLAYER_B']['mark'] = reversed_sanitized_mark
    return True

def player_sign_up():
    choosen_mark = \
        input(f"Hello Player 1, choose your thing ('X' or 'O'); with default as 'X': ").strip()
    set_player_mark(choosen_mark)
    machine_mode =  \
        input(f"Do you want to play against 🤖 : ").strip()
    if machine_mode.lower()[0] == 'y':
        boot_machine()
        return True

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
        show_board()
        game_data["historical_score_data"].append(current_player)
        return rematch_prompt(current_player)
    elif game_data["total_moves"] == 8:
        log("Tie")
        show_board()
        game_data["historical_score_data"].append('TIE')
        return rematch_prompt(current_player)
    else:
        game_data["total_moves"] += 1
        current_player = toggle(current_player, list(player_meta_data.keys()))
        return roll_game(current_player)

def roll_game(current_player='PLAYER_A'):
    print()
    location = None
    current_player_data = player_meta_data[current_player]

    # prompting for grid location until it's something that we can mark.
    if current_player == 'PLAYER_B' and game_data["machine_mode"]:
        location = machine_move()
    else:
        while location not in game_data["available_locations"]:
            current_location = get_player_location(current_player_data['name'], \
                                                    current_player_data['mark'])
            if check_location_integrity(current_location):
                location = int(current_location)
                
    update_location(current_player, location)
    return analyze_match(current_player_data, current_player)
    
if __name__ == "__main__":
    player_sign_up()
    log("Start")
    roll_game()
