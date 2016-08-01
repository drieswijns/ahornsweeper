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
