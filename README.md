# RobotArena 🤖

TODO: Small description + concept

## Hosting the server

First someone needs to host the server (`robotarena_server.py`). The default port is `5901` but you can of course edit it to your liking. It will open up a PyGame Window that shows the position of all robots.

## Implementing the client

Every client needs to import the `Robot` class from `robotarena_client.py`. Just add this to the top of your Python script:

```Python
from robotarena_client import *
```

Now you can access the class and build your own robot. Once it's your robot's turn the server will notify your client and execute your turn callback. The server also sends you the current grid so you can react depending on the other's location. To get your location you can search for your robot on the grid.
Your callback should always return a tuple of exactly two actions. It's also possible to use the same action twice.

### Constants:

```Python
# Actions your robot can do when
# it's turn starts.
MOVE
ATTACK
TURN_LEFT
TURN_RIGHT
```

```Python
# Directions robots can be turned.
# Useful when comparing them.
UP
DOWN
LEFT
RIGHT
```

### Functions:

```Python
# Returns your robot's name.
def get_name(self):
```

```Python
# Returns the size of the grid.
def get_grid_size(self):
```

```Python
# Sets the turn function that gets
# called when it's your robot's turn.
def set_turn(self, callback):

# EXAMPLE:
# Your callback function should always
# return a tuple of two action constants.
# Use the "grid" parameter to look out
# for other robots.
def my_turn(grid):
	return (MOVE, TURN_LEFT)
my_robot.set_turn(my_turn)
```

```Python
# Sets the image of your robot.
def set_image(self, image_path):
```

```Python
# Connects to the server with the
# given IP and port.
def connect(self, ip, port):
```

```Python
# Finally starts your robot.
def start(self):
```

### Example:

Here is a simple robot implementation that will just walk circles and show your location on the grid.
```Python
def get_my_location(grid):
	for i in range(robot.get_grid_size()):
		for j in range(robot.get_grid_size()):
			target_robot = grid[i][j]
			if target_robot and target_robot["name"] == robot.get_name():
				return target_robot["x"], target_robot["y"], target_robot["direction"]

def my_turn(grid):
	x, y, direction = get_my_location(grid, robot.get_name())
	print("My location:\n", "x=", x, "y=", y, "direction:", direction)
	return (MOVE, TURN_LEFT)

my_robot = Robot("MyRobot")
my_robot.connect("127.0.0.1", 5901)
my_robot.set_turn(turn)
my_robot.start()
```
