import redis
import json
import random
import string

user_meta_data = {
    'registered' : False,
    'name': None
}

def publish_data(channel, data, redis_client):
    try:
        redis_client.publish(channel, data)
    except(e):
        print("ERROR: ", e)
    return 

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
def show_board(available_grid):
    grouped_location = [available_grid[k:k+3] for k in range(0, len(available_grid),3)]
    for row in grouped_location:
        row = magic_cols(row)
        print(f"|{row[0]}|{row[1]}|{row[2]}|")
    return True

def prompt_user_info():
    user_name = input("What is your name? : ")
    user_meta_data['name'] = user_name
    return json.dumps({"name": user_name})

def prompt_move():
    move = input("What's your move? : ")
    return json.dumps({"name": user_meta_data['name'], "move": move})

if __name__ == '__main__':
    redis_client = redis.Redis(host='0.0.0.0', port=7001, db=0)
    pubsub = redis_client.pubsub()
    pubsub.subscribe(['match_state', 'available_grid', 'current_player'])
    user_id = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = 7)) 
    publish_data('register_user', user_id, redis_client)
    user_name =  None
    for event in pubsub.listen():
        channel_name = event['channel'].decode('ascii')
        if event['type'] == 'message':
            if (channel_name == 'match_state' and \
                int(event['data']) == 1 and user_meta_data['registered'] == False):
                print('here')
                user_info = prompt_user_info()
                publish_data('user_info', user_info, redis_client)
                user_meta_data['registered'] = True
            elif (channel_name == 'match_state' and \
                event['data'] == 2):
                print("match ended")
            elif (channel_name == 'available_grid'):
                show_board(json.loads(event['data']))
            elif (channel_name == 'current_player' and \
                  event['data'].decode('ascii') == user_meta_data['name']):
                user_move = prompt_move()
                publish_data('move', user_move, redis_client)