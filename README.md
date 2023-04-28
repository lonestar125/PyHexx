# FINAL TODO: (deadline tmrw 19h30)
```
get signed picture and voice authorisations from our parents
fix README, clean repo (add src and stuff) -> last
- see pytris and snowflake

project:
- background ?
- rearrange menu DONE
- push hidden sprite DONE
- fix shitcode DONE


video:
- write script
    - prentation des membres
    - résume du projet
    - démo
- film individually

rapport:
- fix cover image
- finish etapes
- rediger fonctionnement
- rediger ouverture
- analyse critique

Documentation: 
- prerequis d'installation
- explications des bots/game mode
    - random --> checks every move available and uses random.choice
    - easy (1 layer) --> checks every move available and calculates the score for the current player if each move was to be played
    - normal (2 layer) --> uses a tree where each node represents a board and additional info like player, move played etc... calculates every possible move for the player and then the move that would result in the highest score for the enemy player in response. chooses the move with the highest score after the enemy response. 3 layer was initially implemented but was proved to be too slow to use
    - MCTS --> goofy + doesnt work properly + too slow + bad idea + 4 steps: selection, expansion, simulation, backpropagation. essentially plays a bunch of random games and then determines which move is best based on the amount of games won divided by games played for that move, requires a ridiculous (several million) amount of runs (PER MOVE) too spit out a good result, based on the amount of iteration you run, this coud easily go to 30mins per move so completely unusable
- indepth code analysis:
    - dans game --> attend le input, si input display outline, si click on outlined, do move, display nieghbour, end turn --> check victory
    - dans menu --> attend le click d'un bouton
    - dans board editor --> quand click, change status, when menu pressed, do the pathfinding algo, chekc that each player has atleast one tile to start with (uses the get_score function
    - dans info --> utilisation de la fonciton render text pour afficher les infos
    
bug:
situation when on start a player has no possible moves, fix: check that a player has moves by calling the check_moves (not sure of the name) function in a condition during the board editor check phase
```


# Todo

```
(in order of importance):
    
MOST URGENT:
- info screen DONE
- MCTS bot DONE
- docstring DONE
- write video script 

VIDEO:
- film individually and join together (not optimal)
- possible dates ?
    - this friday (21/04)
    - next thursday (27/04)
    - next friday (28/04) (last day to submit) --> this is not optimal as we want to send all the files to jonchery as early as possible (she might not check her mails during the vacation)
OR
- film and stich it up in a imovie or some shit

(in order of importance):
    
    board stuff:
        - display invalid board instead of print DONE
        - reset button in board editor DONE
        - save edited board in a variable (must be a deep copy (possibly without tile objects as idk what happens with those)) DONE
        - reset edited board to its orginial state when game ends DONE
    
    display scores in game DONE
    display winning player for a few seconds before returning to menu DONE

    implement menu (this is implemented as logic but ui MUST be improved)
        - title/banner image/idk
        - rules/info screen --> NOT IMPLEMENTED, add game rules + credits (our names/school/idk)
        - board editor
        - game mode DONE, add MCTS bot once done
        - play
   
    immplement random move bot DONE
    implement 1 layer bot DONE
    implement MCTS bot
 
    Add sfx (maybe)
        - add mute/unmute button on all screens at the bottom right or something
    - End game (win)
    - Move / Clone
    - Conquer
    - Main menu music
    - Button click

```
# Ideas for the rapport
```
- make window resizable/scalable
- further imrpove board editor to be able to load boards and save boards from an external file
- make a self play neural net similar to alphago zero
- improve UI
- add sfx
- add animations
```


