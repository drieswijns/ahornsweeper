Ahornsweeper
============

In this tutorial you will create an automated minesweeper player.
This is an introduction to game playing AI and the ahorn framework.

Minesweeper
-----------
*(Feel free to skip this if you already know the rules of minesweeper)*

Minesweeper is a single player game where you need to find all bomb-free
cells in a grid filled with bombs.

Initially, the grid is completely unknown.

![Unknown grid in minesweeper](/resources/empty.png)

After marking a spot as bomb-free, you'll discover more of the grid.

![Grid in minesweeper](/resources/remaining.png)

A number in a cell represent the number of bombs around that cell.
The goal of the game is to discover all bomb-free cells.

In the next chapter you will look at a general algorithm to solve this game.

Automating Minesweeper
----------------------

Let's say you are presented with the following situation:

    1 1 1
    1 · ·
    1 · ·

And additionally, you know that there is **only one bomb** in the grid. The cell
in the left upper corner is flanked by one bomb, and the center cell is it's
only unknown neighbor, the bomb must be located in that center cell.

    1 1 1
    1 ☆ ·
    1 · ·

And therefore the other three cells can be marked as bomb-free.

Let's look at a more difficult situation

    2 2 1
    · · ·

And additionally, you know that there are **only two bombs** in the grid. This
situation is a bit more difficult as there are multiple bomb configurations that
satisfy the numbers. These configurations are:

    2 2 1    2 2 1
    ☆ ☆ ·    ☆ · ☆

In this situation you'll need to make a guess. The two rightmost cells in the center
rows have an equal probability of being bomb-free. Even when you play this game
perfectly, you'll only have a 50% chance of winning.

Automating this taught process will go as follows:   
* Look at the possible bomb configurations
* For each cell, compute the probability of it being bomb-free
* Mark the cell with the highest probability as bomb-free

Repeat until all bomb-free cells are found.

In the next chapter you will learn how to describe minesweeper in the ahorn framework.

Describing minesweeper in ahorn
-------------------------------

We first need to describe the rules of minesweeper to ahorn. Ahorn splits a game
into two parts:

  1. **State**: this is the bomb configuration, and stores the cells that are marked as bomb-free
  2. **Action**: minesweeper contains only one action: *mark cell as safe*

Start by installing ahorn:

    pip install ahorn

### State
The second step is to describe the state of the game:

    import random
    import ahorn, ahorn.GameBase.State

    grid_width, grid_height = 4, 4  # the size of the grid
    n_bombs = 5  # how many bombs

    class MinesweeperState(ahorn.GameBase.State):
        def __init__(self, player):
            self.player = player  # the player that will solve the game, you will create him later

            # make a matrix for the bomb grid
            self.configuration = [  # True if bomb, false if bomb-free
                [False] * grid_width
            ] * grid_height

            # place the bombs randomly on the grid
            positions = [[i, j] for i in range(grid_height) for j in range(grid_width)]
            for x, y in random.sample(positions, n_bombs):
                self.configuration[x][u] = True

            # make a matrix for to store what the player has discovered
            self.discovered = [  # None if no information is known, otherwise an int counting the neighboring bombs
                [None] * grid_width
            ] * grid.height

        def str(self, player):
            """Return a string representation of the state, showing only information known to the player."""
            return "\n".join([
                " ".join([str(number) for number in row])
                for row in self.discovered
            ])


You know have a place to store the location of the bombs, and the cells marked as bomb-free by the player.

The next thing ahorn needs to know is when the game is finished. Ahorn does this by calling the **is_final** method
of the state.

    ...

    def is_final(self):
        """Return True if the game is over, False if the game is not over."""
        # Any bombs exploded?
        positions = [[i, j] for i in range(grid_height) for j in range(grid_width)]
        for x, y in positions:
            is_marked_bomb_free = self.discovered[x][y] is not None
            is_bomb = self.configuration[x][y]
            if is_bomb and is_marked_bomb_free:
                return True  # the player marked a cell as bomb-free, but there was a bomb

        # Did the player mark all bomb free places ?
        n_marked_bomb_free = 0
        for x, y in positions:
            is_marked_bomb_free = self.discovered[x][y] is not None
            if is_marked_bomb_free:
                n_marked_bomb_free += 1
        n_bomb_free = (grid_width*grid_height) - n_bombs
        if n_marked_bomb_free == n_bomb_free:
            return True  # the player has found all bomb-free cells

        # in all other cases, the game isn't over yet
        return False

We see in the code above that there are only two conditions where the game can be over:

1. a bomb exploded, or
2. all safe cells have been found
