# Trophee NSI
## Fork du [jeu scratch](https://scratch.mit.edu/projects/318837312/)
## [remake](hexxagon.com)
## [original/emulateur](https://www.retrogames.cz/play_710-DOS.php?language=EN)


# Comment faire la liste de la grille?

default board index representation (start from 0 instead of 1)
tile status standardisation:
0: empty
1: player 1 -> blue
2: player 2 -> red
3: blocked/obstacle

2d array (list of list):

[1, 2, 3, 4, 5], 0
[1, 2, 3, 4, 5, 6],             1
[1, 2, 3, 4, 5, 6, 7],          2	
[1, 2, 3, 4, 5, 6, 7, 8],       3
[1, 2, 3, 4, 5, 6, 7, 8, 9],    4
[1, 2, 3, 4, 5, 6, 7, 8],       5
[1, 2, 3, 4, 5, 6, 7],          6
[1, 2, 3, 4, 5, 6],             7
[1, 2, 3, 4, 5],                8

SEE HEXXAGON.JPG

### these are the delta values to be added to the selected tile to get all direct clone/jump neighbours:

[x, y] = [row, column] (this will need to be flipped potentially as the indexes in a 2d array work as y[x])

[-1, 0], [1, 0], [0, -1], [-1, -1], [0, 1], [1, 1] --> direct neighbours/clone tiles

[2, 0], [-2, 0], [-2, -1], [1, -1], [-1, 1], [2, 1], [0, 2], [-1, -2], [-2, -2], [0, 2], [1, 2], [2, 2] --> neighbours (2 tiles away)/jump tiles




# TODO:

#### BASE GAME/pvp with base board
- create a function that creates a hexxagon board with a given radius
- create a function that returns the tile position/[x,y] of a given tile
- create a function that returns the tile status of a given tile
- create a function that indicates if a tile is out of bounds
- create a function that returns the [x,y] position of all cloneable and jumpable tiles
- create a function that checks if the game is won
- create a function that acts as the base game loop and takes in account who's turn it is

#### UI
- flask web app
- create a function that returns the board as a html table


#### POSSIBLITIES/LATER DEVELOPMENT
- ai for the opponent, pytorch ml implementation
- different board layouts/board layout choice
- board creator/modifier (?) (choose size (radius), default tile places, blocked tiles)
- potential to add 4 player mode (?) (not very important)
