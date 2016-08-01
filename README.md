Ahornsweeper
============

In this tutorial you will create a automated minesweeper player.
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

The numbers in the grind represent the number of bombs around that number.
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
            indices = [[i, j] for i in range(grid_height) for j in range(grid_width)]
            for x, y in random.sample(indices, n_bombs):
                self.configuration[x][u] = True

            # make a matrix for to store what the player has discovered
            self.discovered = [  # None if no information is known, otherwise an int counting the neighboring bombs
                [None] * grid_width
            ] * grid.height
