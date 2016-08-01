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

    def get_utility(self, player):
        """Return -1 when a bomb has exploded, +1 otherwise."""
        positions = [[i, j] for i in range(grid_height) for j in range(grid_width)]
        for x, y in positions:
            is_marked_bomb_free = self.discovered[x][y] is not None
            is_bomb = self.configuration[x][y]
            if is_bomb and is_marked_bomb_free:
                return -1  # the player marked a cell as bomb-free, but there was a bomb
        return +1

    def get_random(self, player):
        """Return a possible bomb configuration, based on the information available to the player"""
        new_state = MinesweeperState(self.player)
        # copy the matrix containing the cells marked as safe
        new_state.discovered = [
            [number for number in row]
            for row in self.discovered
        ]

        # use that matrix to find a possible bomb configuration
        # create a new problem in pulp
        # for more information check out the pulp documentation
        prob = pulp.LpProblem("MineSweeper", pulp.LpMinimize)
        prob.mines = pulp.LpVariable.dicts(
            "Mine",
            (range(grid_height),range(grid_width)),
            0,1,
            pulp.LpInteger
        )
        prob += 0  # Arbitrary objective function, we are only looking at constraints

        # add a maximum number of mines
        positions = [[i, j] for i in range(grid_height) for j in range(grid_width)]
        prob += pulp.lpSum([
            prob.mines[x][y]
            for x, y
            in positions
        ]) == n_bombs

        # add constraints based on the maximum number of mines around cells marked as bomb-free
        for x, y in positions:
            count = new_state.discovered[i][j]
            if count is None:  # cell has not been marked as bomb-free
                continue  # skip
            neighbors = [
                [x+dx, y+dy]
                for dx in [-1, 0, 1]
                for dy in [-1, 0, 1]
                if not (dx == 0 and dy == 0)
            ]
            prob += pulp.lpSum([
                prob.mines[ni][nj]
                for nx, ny
                in neighbors
            ]) == count

        # the problem has been described, including all constraints
        # now pulp can solve it
        prob.solve()
        solution = [
            [bool(pulp.value(prob.mines[i][j])) for j in range(grid_width)]
            for i in range(grid_height)
        ]
        new_state.configuration = solution
        return new_state
