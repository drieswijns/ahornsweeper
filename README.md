Ahornsweeper
============

In this 1 hour tutorial you will create an automated minesweeper player.
This is an introduction to game playing AI and the ahorn framework, and assumes
you already know how to program in python.

Minesweeper
-----------
*(Feel free to skip this chapter if you already know the rules of minesweeper)*

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

And additionally, you know that there is **only one bomb** in the grid. As the cell
in the left upper corner is flanked by only one bomb, and the center cell is it's
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

Automating this taught process:   
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
                [False for _ in range(grid_width)]
                for __ in range(grid_height)
            ]

            # place the bombs randomly on the grid
            positions = [[i, j] for i in range(grid_height) for j in range(grid_width)]
            for x, y in random.sample(positions, n_bombs):
                self.configuration[x][y] = True

            # make a matrix for to store what the player has discovered
            self.discovered = [  # None if no information is known, otherwise an int counting the neighboring bombs
                [None for _ in range(grid_width)]
                for __ in range(grid_height)
            ]

        def str(self, player):
            """Return a string representation of the state, showing only information known to the player."""
            return "\n".join([
                " ".join([str(number) if number is not None else "?" for number in row])
                for row in self.discovered
            ])


You now have a place to store the location of the bombs, and the cells marked as bomb-free by the player.
You also created a string representation of all the information the players knows about the state.

The next thing ahorn needs to know is when the game is finished. Ahorn does this by calling the **is_final** method
on the state.

    (continued)
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

At the end of the game, ahorn needs to assign a score to the player. A typical scoring
scheme is +1 when the player has won, and -1 when the player has lost, i.e. a bomb exploded.
In ahorn the scoring is done in the **get_utility** method.

    (continued)
    def get_utility(self, player):
        """Return -1 when a bomb has exploded, +1 otherwise."""
        positions = [[i, j] for i in range(grid_height) for j in range(grid_width)]
        for x, y in positions:
            is_marked_bomb_free = self.discovered[x][y] is not None
            is_bomb = self.configuration[x][y]
            if is_bomb and is_marked_bomb_free:
                return -1  # the player marked a cell as bomb-free, but there was a bomb
        return +1

Now comes the difficult part, in the previous chapter we discussed the general algorithm
for solving the grid. The algorithm required you to find the bomb configurations that are possible
based on the information the player has gained about the board. This problem can be expressed
as a linear program, and we'll use the python module **pulp** to solve it.

Install pulp

    pip install pulp

In ahorn the **get_random** method must return a possible game state, based on the
information available to the player. In technical terms, all the possible states that
are possible given the player's information are called the **information set**. With the
**get_random** method, a player can **sample from the information set**.

    (continued)
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
        prob = pulp.LpProblem("MineSweeper", pulp.LpMinimize)
        prob.mines = pulp.LpVariable.dicts(
            "Mine",
            (range(grid_height),range(grid_width)),
            0,1,
            pulp.LpInteger
        )
        prob += 0  # Arbitrary objective function, we are only looking at constraints

        # add a maximum number of mines
        prob += pulp.lpSum([
            prob.mines[x][y]
            for x, y
            in positions
        ]) == n_bombs

        # add constraints based on the maximum number of mines around cells marked as bomb-free
        for x, y in positions:
            count = new_state.discovered[x][y]
            if count is None:  # cell has not been marked as bomb-free
                continue  # skip
            neighbors = [
                [x+dx, y+dy]
                for dx in [-1, 0, 1]
                for dy in [-1, 0, 1]
                if (
                    not (dx == 0 and dy == 0)
                    and (x+dx >= 0 and x+dx < grid_height)
                    and (y+dy >= 0 and y+dy < grid_width)
                )
            ]
            self.prob += pulp.lpSum([
                self.prob.mines[nx][ny]
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

The **get_random** method will return a new state, with a
bomb-configuration that is possible given the bomb-free cells that have been discovered
by the player.

**But** it will always return the same bomb-configuration. And remember, you needed to
sample from __all__ configurations, so you will have to make another slight adjustment to the **get_random**
method.

Add this to **MinesweeperState**'s __init__:

    (continued)
    def __init__(self, player):
        # ...
        self.prob = None  # Store the LP problem for successive runs of the get_random method

Make **get_random** use the stored problem if possible:

    (continued)
    def get_random(self, player):
      # ...
      if not self.prob:
          self.prob = pulp.LpProblem("MineSweeper", pulp.LpMinimize)

After pulp has found a solution, make sure it will not return the same solution again

    (continued)
    def get_random(self, player):
        # ...
        self.prob.solve()
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
        # ...

Once pulp has found all solutions, return from the beginning

    (continued)
    def get_random(self, player):
      # ...
      self.prob.solve()
      if not pulp.LpStatus[self.prob.status] == "Optimal":
          # We have found all solutions, restart
          self.prob = None
          return self.get_random(player)

      # ...

And there you have it. For any possible board discovered by the player, ahorn can use
the **get_random** method to find all possible bomb configurations.

To finalize the **MinesweeperState** there are three bookkeeping methods required by ahorn.

    (continued)
    def get_actor(self):
        """Return the player"""
        return self.player

    def get_players(self):
        """Return all players, only one in the case of minesweeper"""
        return [self.player]

    def copy(self, other):
          """Deep copy the contents of other to self"""
          self.configuration = [
              [is_bomb for is_bomb in row]
              for row in other.configuration
          ]

          self.discovered = [
              [count for count in row]
              for row in other.discovered
          ]

You have now completed the **MinesweeperState**, it includes the bomb configuration,
the information found by the player, the game's stop conditions (**is_final**), the game's
scoring mechanism (**get_utility**), and a way to translate the information the players has
to possible bomb configurations (**get_random**).

The **State** was the first part of the game description. You will create the second part, the **Actions**,
in the next section.

### Actions

In minesweeper, there is only one action available to the player: mark a cell as safe.

Start by subclassing **ahorn.GameBase.Action**:

    class MarkBombFree(ahorn.GameBase.Action):
        def __init__(self, x, y):
            self.x = x  # cell row
            self.y = y  # cell column

        def __str__(self):
            return "Mark bomb-free in ({}, {})".format(self.x, self.y)

You need to tell ahorn how an action influences a state. This is done by implementing the **execute** method.

    (continued)
    def execute(self, state):
        """This action will modify a the state by adjusting the discovered matrix"""

        if state.discovered[self.x][self.y] is not None:
                return state

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
            if (
                not (dx == 0 and dy == 0)
                and (self.x+dx >= 0 and self.x+dx < grid_height)
                and (self.y+dy >= 0 and self.y+dy < grid_width)
            )
        ]
        bombs_around = sum([
            1
            for nx, ny in neighbors
            if state.configuration[nx][ny]
        ])
        state.discovered[self.x][self.y] = bombs_around

        # If the neighboring cells are also empty, cascade the discovery
        if bombs_around == 0:
                for nx, ny in neighbors:
                    state = MarkBombFree(nx, ny).execute(state)
        return state

As you can see, the **execute** method does two things:

1. If there is a bomb in the cell the players wants to mark as bomb-free, it will explode
2. Else, it will count the number of neighboring bombs, and put the count in the cell

The *State* and the *Actions* are now completely defined. You only need a way to link them, which you will do in the next chapter.

### Linking **State** and **Actions**
Ahorn knows which actions are possible in a given state by calling the **get_legal_actions** method.
The possible actions in minesweeper are easy: the player can mark any previously unmarked cell as bomb-free.
The cell might explode, or it might not, but trying it out is always a legal action.

    class MinesweeperState(ahorn.GameBase.State):
        # ...
        def get_legal_actions(self, actor):
              """The player can mark all previously unmarked cells as bomb-free"""
              actions = []
              positions = [[i, j] for i in range(grid_height) for j in range(grid_width)]
              for x, y in positions:
                  if self.discovered[x][y] is None:
                      actions.append(MarkBombFree(x, y))
              return actions

Playing your first game
-----------------------

You've reached your first milestone! You've taught ahorn how to play minesweeper.

    if __name__ == "__main__":
        import ahorn.Actors
        player = ahorn.Actors.RandomPlayer()
        initial_state = MinesweeperState(player)
        controller = ahorn.Controller(
            initial_state,
            verbose=True  # print to screen
        )
        controller.play()

If you put this at the bottom of your file, and execute it, you might get an output like this:

    (venv)john@doe:~$ python minesweeper.py
    ? ? ? ?
    ? ? ? ?
    ? ? ? ?
    Mark bomb-free in (2, 0)
    ? ? ? ?
    ? ? ? ?
    0 ? ? ?
    ? ? ? ?
    Mark bomb-free in (2, 2)
    ? ? ? ?
    ? ? ? ?
    0 ? 3 ?
    ? ? ? ?
    Mark bomb-free in (2, 3)
    ? ? ? ?
    ? ? ? ?
    0 ? 3 ☆
    ? ? ? ?
    Points: -1

Quite a disappointing result. The player chooses very bad actions. Let's
quantify just how disappointing the **RandomPlayer** player is.

Replace the script by:

    if __name__ == "__main__":
        import ahorn.Actors
        player = ahorn.Actors.RandomPlayer()

        n_games = 100
        points = 0
        for _ in range(n_games):
            initial_state = MinesweeperState(player)
            controller = ahorn.Controller(
                initial_state,
                verbose=False
            )
            final_state = controller.play()
            points += final_state.get_utility(player)

        print("Games played: {}".format(n_games))
        print("Total points: {}".format(points))
        print("Average points: {}".format(points/n_games))

You will most probably get the following result:

    (venv) john@doe:~$ python minesweeper.py
    Games played: 100
    Total points: -100
    Average points: -1.0

The random player lost all the games! Looks like randomly clicking on cells
isn't a very good strategy. Let's see if you can do better. In the next chapter
you will be creating your own **Player** which (hopefully) plays better than the **RandomPlayer**

Player
------

You will be implementing the algorithm discussed in the first chapter as a **Player** in ahorn.

Start by subclassing **ahorn.Actors.Player***:

    import ahorn.Actors

    class MinesweeperPlayer(ahorn.Actors.Player):
        def __init__(self):
            pass

        def get_action(self, state):
            # ...
            return action

A player only needs one method: **get_action**. Based on the state that is passed to that method,
the actor returns the best action he thinks he should take in that situation.

You want the **MinesweeperPlayer** to look at different possible bomb-configurations to
estimate the probability of a cell being bomb-free. Ideally it would look at all the possible configurations, but that would be too slow.
Instead, we will make **MinesweeperPlayer** look at only a few, and hope the result of those
few are representable for the entire set.

    class MinesweeperPlayer(ahorn.GameBase.Player):
        def __init__(self):
            pass

        def get_action(self, state):
            simulations_per_action = 15  # how many configurations to look at for each given action
            legal_actions = state.get_legal_actions(self)
            points = {
                action: 0
                for action in legal_actions
            }

            for action in legal_actions:
                for _ in range(simulations_per_action):
                    possible_state = state.get_random(self)
                    possible_state = action.execute(possible_state)
                    points[action] += possible_state.get_utility(self)

            best_action = max(points.items(), key=lambda action_points: action_points[1])[0]

            return best_action

When you let **MinesweeperPlayer** play a couple of games, you'll get a result similar to

    (venv) john@doe:~$ python minesweeper.py
    Games played: 100
    Total points: -50
    Average points: -0.5

Which is slightly better than the random player.

## Conclusions
You've added a new game, minesweeper, to ahorn and you've created your first player.
You now know how ahorn works, and can start creating your own AI.

Here are a couple ideas for your future AI


2. [multi-armed bandid strategies](https://en.wikipedia.org/wiki/Multi-armed_bandit)
3. [Q-learning](https://en.wikipedia.org/wiki/Q-learning)
4. multi-player games, with or without adversaries

Have fun!
