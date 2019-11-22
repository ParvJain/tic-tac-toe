player_meta_data = {}

game_data = {
    "machine_mode": False,
    "board_dimension": 3,
    "available_locations" : list(range(1,10)),
    "winners_cheat_sheet" : [[1,2,3], [4,5,6], [7,8,9], # vertical lines
                             [1,4,7], [2,5,8], [3,6,9], # horizontal lines
                             [1,5,9], [3,5,7]], # diagonal lines,
    "total_moves" : 0,
    "historical_score_data": []
}
