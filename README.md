Ahornsweeper
============

In this tutorial you will create a automated minesweeper player.
This is an introduction to game playing AI and the ahorn framework.

Minesweeper
-----------
*(Feel free to skip this if you already know the rules of minesweeper)*

Minesweeper is a single player game where you need to find all safe
spots in a grid filled with bombs.

Initially, the grid is completely unknown.
![Unknown grid in minesweeper](/resources/empty.png)

After marking a spot as safe, you'll discover more of the grid.
![Grid in minesweeper](/resources/remaining.png)

The numbers in the grind represent the number of bombs around that number.
The goal of the game is to mark all spots without a bomb as safe.
