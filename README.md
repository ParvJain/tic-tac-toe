## How to start the game?

`$ python3 main.py`

## Implimentation flow

0. Initialize Program.
1. Ask for Player 1 and Player 2 identity and preffered Symbol to Player 1 either X or O.
2. Print out 3 x 3 grid given values from available location
3. ask player one for the location he want to mark, validate is location and update available_locations along with player's location array.
4. check for win; break if win : continue if not
5. increment move by 1, switch player and goto: 2
6. check if total moves are 9 declare a tie.
7. prompt a rematch -> reset scores and meta data.


## Valid Inputs

1. Player 1 is a decider for Player 2 mark as well, if he doesn't choose O Player 2 gets it and vice-versa. Player identity is mandatory as of now.
2. valid input for players move is Number - that specify location of the grid, everything except it is not valid and error will be thrown.


## What defines a win?

Given a 3 x 3 grid with the pre-filled values from 1 to 9 marked left to right, here are the possible "win" cases:

```
[[1,2,3], [4,5,6], [7,8,9], # vertical lines
[1,4,7], [2,5,8], [3,6,9], # horizontal lines
[1,5,9], [3,5,7]] # diagonal lines
```

## Additional Features

1. If you've won the round, next round looser will have an advantage by making the first move.
2. If it's a tie, alternative player will have advantage.

### Machine mode

Machine mode works on two major priciples,
1. Defend - Machine should defend any mark which allows opponent to win or to make any advancement towards wining
2. Attack - make advancements towards winning.

which means after every step user takes it runs an analysis towards making it's next move by:
1. getting the available slots (moves).
2. compare machine and opponent's marked data against win scenarios to,
3. rank each possible move with following levels:
    1. 0 - no affect on attack or defensiveness 
    2. 1,2 - advancement towards making a win/defend
    3. 3 [Power Move] - win or stop opponent from winning
4. once all moves are ranked; top rankers are picked up and randomly choosen.
