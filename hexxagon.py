def drawMap():
    """
    None --> None
    Draws the inital map depending on the chosen size of the hexagon's side.
    """
    numRow = int(input("Size of the hexagon's side? "))
    rows = [numRow - abs(i - (numRow//2 + 1)) for i in range(1, numRow + 1)]
    for column in rows:
        print(" " * (numRow - column), end="")
        for row in range(column):
            print(' O ', end = "")
        print()

def getPos():
    """
    ... --> ...
    Returns the position (x and y) of a given tile.
    """
    print()

def getStatus():
    """
    ... --> ...
    Returns the status of a given tile.
    """
    print()

def isBound():
    """
    ... --> ...
    Indicates if a given tile is out of bouds or not.
    """
    print()

def playOptions():
    """
    ... --> ...
    Returns the positions of all the playable options. (x,y of all the jumpable and cloneable tiles)
    """
    print()
