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
-1: nothing there, blocked, hidden


set starting tiles/colors on those tiles +++DONE+++

todo next:
    implement odd n1 and n2 +++DONE+++
    implement clear outline when turn ends +++DONE+++
    implement turns +++DONE+++
    implement score
    implement victory check at the end of each turn

logic:
when click
    if the tile has current players color:
        calculate outlines +++DONE+++
            --> manually create list of deltas (n1 deltas and n2 deltas for neighbours +1 and neighbours +2) +++DONE+++
            --> lists of both jumpable and clonable tiles made my combining current tile indexes with deltas +++DONE+++
        display outlines +++DONE++
            --> draw function +++DONE+++
    
    if the tile has jumpable status:
        --> make selected tile status 0 (empty) +++DONE+++
        --> make clicked tile have current player's color +++DONE+++
        check neighbours using the n1 lists: +++DONE+++
            --> convert all the non current player's neighbouring tiles to current player +++DONE+++
        --> recalculate scores
        --> end turn +++DONE+++
        --> check victory
        --> changes current player
        
    
    if the tile has clonable status:
        --> make clicked tile have current player's color +++DONE+++
        check neighbours using the n1 lists: +++DONE+++
            --> convert all the non current player's neighbouring tiles to current player +++DONE+++
        --> recalculate scores
        --> end turn
        --> check victory
        --> changes current player

stuff for later (in order of importance):
    make new assets not ripped from the original game   
    add menu
    add bots/algorithm/ai
    make random hidden tiles
    add sounds
    
    
