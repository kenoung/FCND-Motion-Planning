from enum import Enum
from queue import PriorityQueue
import numpy as np


def create_grid(data, drone_altitude, safety_distance):
    """
    Returns a grid representation of a 2D configuration space
    based on given obstacle data, drone altitude and safety distance
    arguments.

    Parameters
    ----------
    data : 2D numpy array
    Data parsed from colliders.csv.

    drone_altitude : numeric value (int or float)
    Height of the drone. Obstacles below this height will be ignored.

    safety_distance : numeric value (int or float)
    Minimum distance allowed between drone and obstacle.

    Returns
    -------
    grid : 2D numpy array
    2D array of values containing only 1s and 0s, where 1s indicate no-go zones.

    north_min : int
    Minimum north coordinate.

    east_min : int
    Minimum east coordinate.
    """

    # minimum and maximum north coordinates
    north_min = np.floor(np.min(data[:, 0] - data[:, 3]))
    north_max = np.ceil(np.max(data[:, 0] + data[:, 3]))

    # minimum and maximum east coordinates
    east_min = np.floor(np.min(data[:, 1] - data[:, 4]))
    east_max = np.ceil(np.max(data[:, 1] + data[:, 4]))

    # given the minimum and maximum coordinates we can
    # calculate the size of the grid.
    north_size = int(np.ceil(north_max - north_min))
    east_size = int(np.ceil(east_max - east_min))

    # Initialize an empty grid
    grid = np.zeros((north_size, east_size))

    # Populate the grid with obstacles
    for i in range(data.shape[0]):
        north, east, alt, d_north, d_east, d_alt = data[i, :]
        if alt + d_alt + safety_distance > drone_altitude:
            obstacle = [
                int(np.clip(north - d_north - safety_distance - north_min, 0, north_size-1)),
                int(np.clip(north + d_north + safety_distance - north_min, 0, north_size-1)),
                int(np.clip(east - d_east - safety_distance - east_min, 0, east_size-1)),
                int(np.clip(east + d_east + safety_distance - east_min, 0, east_size-1)),
            ]
            grid[obstacle[0]:obstacle[1]+1, obstacle[2]:obstacle[3]+1] = 1

    return grid, int(north_min), int(east_min)


# Assume all actions cost the same.
class Action(Enum):
    """
    An action is represented by a 3 element tuple.

    The first 2 values are the delta of the action relative
    to the current grid position. The third and final value
    is the cost of performing the action.
    """

    WEST = (0, -1, 1)
    EAST = (0, 1, 1)
    NORTH = (-1, 0, 1)
    SOUTH = (1, 0, 1)
    NORTHWEST = (-1, -1, 2**0.5)
    NORTHEAST = (-1, 1, 2**0.5)
    SOUTHWEST = (1, -1, 2**0.5)
    SOUTHEAST = (1, 1, 2**0.5)

    @property
    def cost(self):
        return self.value[2]

    @property
    def delta(self):
        return (self.value[0], self.value[1])


def is_valid_node(grid, node):
    """Returns True if given node is a valid location"""
    n, m = grid.shape[0] - 1, grid.shape[1] - 1
    x, y = node
    if x < 0 or x > n or y < 0 or y > m:
        return False

    if grid[x, y] == 1:
        return False

    return True


def valid_actions(grid, current_node):
    """
    Returns a list of valid actions given a grid and current node.
    """
    actions = list(Action)
    x, y = current_node

    # check if the node is off the grid or
    # it's an obstacle
    valid_action_lst = []
    for action in actions:
        da = action.delta
        next_node = (x + da[0], y + da[1])
        if is_valid_node(grid, next_node):
            valid_action_lst.append(action)

    return valid_action_lst


def a_star(grid, h, start, goal):
    """
    Returns a path and its associated cost by using A* search.

    Parameters
    ----------
    grid : 2D array
    Grid generated using create_grid function. Points marked 1 represent areas that the drone cannot enter.

    h : function
    Heuristic function that takes in two coordinates and returns the cost of travelling between them

    start : tuple of 2 elements
    Start coordinate

    end : tuple of 2 elements
    End coordinate
    """

    path = []
    path_cost = 0
    queue = PriorityQueue()
    queue.put((0, start))
    visited = set(start)

    branch = {}
    found = False
    
    while not queue.empty():
        item = queue.get()
        current_node = item[1]
        if current_node == start:
            current_cost = 0.0
        else:              
            current_cost = branch[current_node][0]
            
        if current_node == goal:        
            print('Found a path.')
            found = True
            break
        else:
            for action in valid_actions(grid, current_node):
                # get the tuple representation
                da = action.delta
                next_node = (current_node[0] + da[0], current_node[1] + da[1])
                branch_cost = current_cost + action.cost
                queue_cost = branch_cost + h(next_node, goal)
                
                if next_node not in visited:                
                    visited.add(next_node)
                    branch[next_node] = (branch_cost, current_node, action)
                    queue.put((queue_cost, next_node))
             
    if found:
        # retrace steps
        n = goal
        path_cost = branch[n][0]
        path.append(goal)
        while branch[n][1] != start:
            path.append(branch[n][1])
            n = branch[n][1]
        path.append(branch[n][1])
    else:
        print('**********************')
        print('Failed to find a path!')
        print('**********************')
        return [], 0
    return path[::-1], path_cost



def heuristic(position, goal_position):
    return np.linalg.norm(np.array(position) - np.array(goal_position))

