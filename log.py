import logging 

log_config = {
    "MethodNotSupported" : {"level": 40,
                            "message": "Method not supported for more than one choice"},
    "InvalidChoice":       {"level": 40,
                            "message": "Choices doesn't have your current state"},
    "NaN":                 {"level": 40,
                            "message": "You need to choose from available numbers 🔢 on board to mark your location"},
    "OutOfRange":          {"level": 40,
                            "message": "You can run but can't hide 👟, choose a number that is available"},
    "Won":                 {"level": 20,
                            "message": "You have won this match 🏆, rematch?"},
    "Tie":                  {"level": 20,
                            "message": "You've both outsmarted each other, 🤼 try again?"},
    "End":                  {"level": 20,
                            "message": "Hope you had as much fun 👻, as I had while writing this."},
    "Start":                {"level": 20,
                            "message": "Match Started! 🏁"}
}


logging.basicConfig(filename="logfile.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='w') 
logger = logging.getLogger() 
logger.setLevel(logging.DEBUG) 

def log(case):
    print(log_config[case]['message'])
    logger.log(log_config[case]['level'], log_config[case]['message'])
