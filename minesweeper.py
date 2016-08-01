import random
import ahorn, ahorn.GameBase.State, ahorn.GameBase.Action

grid_width, grid_height = 4, 4  # the size of the grid
n_bombs = 5  # how many bombs


class MarkBombFree(ahorn.GameBase.Action):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "Mark bomb-free in ({}, {})".format(self.x, self.y)

    def execute(self, state):
        """This action will modify a state.

        Return the modified state."""
        # Is there a bomb in the place we want to mark as safe?
        is_bomb = state.configuration[self.x][self.y]
        if is_bomb:
            state.discovered[self.x][self.y] = "☆"  # BOOM, player exploded a bomb
            return state

        # There was no bomb, we need to find the number of bombs in this cell's neighborhood
        neighbors = [
            [self.x+dx, self.y+dy]
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
            if not (dx == 0 and dy == 0)
        ]
        bombs_around = sum([
            1
            for nx, ny in neighbors
            if state.configuration[nx][ny]
        ])
        state.discovered[self.x][self.y] = bombs_around
        return state

    def __str__(self):
        return "Mark safe in ({}, {})".format(self.i, self.j)


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

        self.prob = None  # Store the LP problem for successive runs of the get_random method

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
        positions = [[i, j] for i in range(grid_height) for j in range(grid_width)]
        # copy the matrix containing the cells marked as safe
        new_state.discovered = [
            [number for number in row]
            for row in self.discovered
        ]

        # use that matrix to find a possible bomb configuration
        # create a new problem in pulp
        # for more information check out the pulp documentation
        if not self.prob:
            self.prob = pulp.LpProblem("MineSweeper", pulp.LpMinimize)
            self.prob.mines = pulp.LpVariable.dicts(
                "Mine",
                (range(grid_height),range(grid_width)),
                0,1,
                pulp.LpInteger
            )
            self.prob += 0  # Arbitrary objective function, we are only looking at constraints

            # add a maximum number of mines
            self.prob += pulp.lpSum([
                self.prob.mines[x][y]
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
                self.prob += pulp.lpSum([
                    self.prob.mines[ni][nj]
                    for nx, ny
                    in neighbors
                ]) == count

        # the problem has been described, including all constraints
        # now pulp can solve it
        self.prob.solve()

        if not pulp.LpStatus[prob.status] == "Optimal":
            # We have found all solutions
            return None

        solution = [
            [bool(pulp.value(self.prob.mines[i][j])) for j in range(grid_width)]
            for i in range(grid_height)
        ]

        # make sure pulp doesn't return the same solution again
        self.prob += pulp.lpSum([
            self.prob.mines[i][j]
            for i, j in positions
            if solution[i][j]
        ]) <= self.n_bombs - 1

        new_state.configuration = solution
        return new_state

    def get_actor(self):
        """Return the player"""
        return self.player

    def get_players(self):
        """Return all players, only one in the case of minesweeper"""
        return [self.player]

    def get_legal_actions(self, actor):
        """The player can mark all previously unmarked cells as bomb-free"""
        actions = []
        positions = [[i, j] for i in range(grid_height) for j in range(grid_width)]
        for x, y in positions:
            if self.counts[x][y] is None:
                actions.append(MarkBombFree(x, y))
        return actions
