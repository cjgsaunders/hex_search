import multiprocessing
import time
from math import cos, pi, sin, sqrt, dist
import threading
import pygame

# -------------- changeable---------------------
# Adjust size of hex, width of grid and height of grid
COLS = 24
ROWS = 32

hex_width = 40

# -------------- changeable finished------------

# intelligent search heuristic
# 1 is euclidean distance
# 2 is Manhattan distance
heuristic_setting = 2

# Math to draw variable sized hex grids. Do not change---------------
hex_quarter_width = hex_width // 4
hex_radius = hex_width // 2  # 2 * distance center-corner
hex_height = sqrt(3) * hex_radius  # sqrt(3) * distance center-corner
horizontal_distance = hex_width * 1.5  # 3/4 * tile_width
vertical_distance = hex_height
offset_x = hex_width * 0.75
offset_y = hex_height // 2
width = int((COLS * horizontal_distance) + (hex_radius / 2))
height = int((ROWS * hex_height) + hex_height // 2)
screen = pygame.display.set_mode((width, height))
size = hex_radius

# Colors
WHITE = (255, 255, 255)
GREY = (110, 110, 110)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Node():
    def __init__(self, x_in, y_in, x_coord_in, y_coord_in):
        self.color = WHITE
        self.neighbours = [None, None, None, None, None, None]  # used for moving by keyboard
        self.algorithm_neighbours = []  # used with the search algorithm
        self.parent = []  # reconstructs the path
        self.x = x_in
        self.y = y_in
        self.x_coord = x_coord_in
        self.y_coord = y_coord_in
        self.wall = False
        self.f = 0
        self.g = 0
        self.h = 0

    def change_col(self):
        self.color = BLACK

    def draw(self):
        draw_hexagon(screen, self.color, 6, hex_radius,
                     ((self.x / 2) * horizontal_distance + hex_radius, self.y * vertical_distance + hex_radius), 0)

    def make_start(self):
        self.color = GREEN

    def make_end(self):
        self.color = RED

    def make_wall(self):
        self.color = BLACK
        self.wall = True

    def make_path(self):
        self.color = BLUE

    def make_visited(self):
        self.color = GREY

    def make_frontier(self):
        self.color = PURPLE

    def reset(self):
        self.color = WHITE
        self.wall = False

    def add_neighbours(self, grid_in):
        self.algorithm_neighbours = []

        if self.y_coord > 1 and (grid_in[self.x_coord][self.y_coord - 2]).wall is False:
            self.neighbours[0] = (grid_in[self.x_coord][self.y_coord - 2])  # add tile above
            self.algorithm_neighbours.append((grid_in[self.x_coord][self.y_coord - 2]))
        else:
            self.neighbours[0] = None

        if self.y_coord >= 1 and self.x_coord < COLS * 2 - 1 and (
                grid_in[self.x_coord + 1][self.y_coord - 1]).wall is False:
            self.neighbours[1] = (grid_in[self.x_coord + 1][self.y_coord - 1])  # add tile above-right
            self.algorithm_neighbours.append(grid_in[self.x_coord + 1][self.y_coord - 1])
        else:
            self.neighbours[1] = None

        if self.y_coord <= (ROWS * 2) - 2 and self.x_coord < COLS * 2 - 1 and grid_in[self.x_coord + 1][
            self.y_coord + 1].wall is False:
            self.neighbours[2] = (grid_in[self.x_coord + 1][self.y_coord + 1])  # add tile right-below
            self.algorithm_neighbours.append(grid_in[self.x_coord + 1][self.y_coord + 1])

        else:
            self.neighbours[2] = None

        if self.y_coord < (ROWS * 2) - 2 and (grid_in[self.x_coord][self.y_coord + 2]).wall is False:
            self.neighbours[3] = (grid_in[self.x_coord][self.y_coord + 2])  # add tile below
            self.algorithm_neighbours.append(grid_in[self.x_coord][self.y_coord + 2])
        else:
            self.neighbours[3] = None

        if self.y_coord <= (ROWS * 2) - 2 and self.x_coord > 0 and (
                grid_in[self.x_coord - 1][self.y_coord + 1]).wall is False:
            self.neighbours[4] = (grid_in[self.x_coord - 1][self.y_coord + 1])  # add tile below-left
            self.algorithm_neighbours.append(grid_in[self.x_coord - 1][self.y_coord + 1])
        else:
            self.neighbours[4] = None

        if self.x_coord > 0 and self.y_coord > 0 and (grid_in[self.x_coord - 1][self.y_coord - 1]).wall is False:
            self.neighbours[5] = (grid_in[self.x_coord - 1][self.y_coord - 1])  # add tile below-left
            self.algorithm_neighbours.append(grid_in[self.x_coord - 1][self.y_coord - 1])
        else:
            self.neighbours[5] = None


def update_single_neighbours(grid_in, node_in):
    for item in node_in.neighbours:
        try:
            item.add_neighbours(grid_in)
        except AttributeError:
            pass


def update_neighbours(grid_in):
    for row in grid_in:
        for item in row:
            try:
                item.add_neighbours(grid_in)
            except AttributeError:
                pass


def make_hex_node_grid_new():
    grid = []

    for x in range(0, COLS * 2):
        grid.append([])
        for y in range(0, ROWS * 2):
            grid[x].append([])

    for x_even in range(0, COLS * 2, 2):
        for y_even in range(0, ROWS * 2, 2):
            node = Node(x_even, y_even / 2, x_even, y_even)
            grid[x_even][y_even] = node

    for x_odd in range(1, COLS * 2, 2):
        for y_odd in range(1, ROWS * 2, 2):
            node = Node(x_odd, y_odd / 2, x_odd, y_odd)
            grid[x_odd][y_odd] = node

    return grid


def draw_new(grid_in):
    for row in grid_in:
        for hex_node in row:
            try:
                hex_node.draw()
            except AttributeError:
                # every other index is empty
                # cant be drawn
                pass

    draw_hex_grid()

    pygame.display.update()


def draw_hexagon(surface, color, vertex_count, radius, position, fill):
    n, r = vertex_count, radius
    x, y = position
    pygame.draw.polygon(surface, color, [
        (x + r * cos(2 * pi * i / n), y + r * sin(2 * pi * i / n))
        for i in range(n)
    ], fill)


def draw_hex_grid():
    for i in range(0, COLS):
        for j in range(ROWS):
            draw_hexagon(screen, GREY, 6, hex_radius,
                         (i * horizontal_distance + hex_radius, j * vertical_distance + hex_radius), 1)

            draw_hexagon(screen, GREY, 6, hex_radius, (
                i * horizontal_distance + offset_x + hex_radius, j * vertical_distance + offset_y + hex_radius), 1)


def move_hex(direction, start_in):
    try:
        if start_in.neighbours[direction] is not None:
            start_in.neighbours[direction].make_start()
            start_in.reset()
            return start_in.neighbours[direction]

        else:
            return start_in
    except AttributeError:
        pass


def get_mouse_pos(pos_in):
    x, y = pos_in

    col_width = width // (COLS * 2)  # DONE
    col_height = height // ROWS

    adjusted_x = x // col_width
    # The code here controles selecting the hexagons
    # There is overlap between the hexagons
    # the sweet spot is a small rectangle in the hexagon which solves the overlap
    sweet_spot_start = hex_quarter_width + ((hex_quarter_width * 3) * adjusted_x)
    sweet_spot_finish = ((hex_quarter_width * 3) * (adjusted_x + 1))
    if sweet_spot_start < x < sweet_spot_finish:
        final_x = adjusted_x
    else:
        final_x = None

    # if statement offsets the y for odd columns
    if adjusted_x == 0 or adjusted_x % 2 == 0:
        adjusted_y = (y // col_height)
        adjusted_y = adjusted_y * 2
        print(final_x, adjusted_y)
        return final_x, adjusted_y
    else:
        adjusted_y = (y + (hex_height // 2)) // col_height
        adjusted_y = adjusted_y * 2 - 1
        print(final_x, int(adjusted_y))
        return final_x, int(adjusted_y)


def reset_grid(grid_in):
    for row in grid_in:
        for item in row:
            try:
                item.reset()
            except AttributeError:
                pass


def heuristic(a, b, heuristic_in):
    if heuristic_in == 1:
        # euclidean distance
        d = dist((a.x, a.y), (b.x, b.y))
    else:
        # Manhattan distance
        d = abs(a.x - b.x) + abs(a.y - b.y)
    return d


def a_star(grid_in, start_in, end_in, heuristic_in):
    visited = set()
    frontier = [start_in]
    print(grid_in[0][0])

    show_path = True

    while True:
        if frontier:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            winner = 0

            for i in range(len(frontier)):
                if frontier[i].f < frontier[winner].f:
                    winner = i

            current = frontier[winner]

            # Draw the path in real time
            path = []
            temp_goal = current
            path.append(temp_goal)
            while temp_goal.parent:
                path.append(temp_goal.parent)
                temp_goal = temp_goal.parent

            for item in path:
                item.make_path()
                item.draw()
                start_in.make_start()

            draw_new(grid_in)

            # Goal check
            if current == end_in:
                end_in.make_end()
                item.draw()
                print("Done")
                break

            # This removes the outdated blue from the previous loop
            for item in visited:
                item.make_visited()
                item.draw()

            frontier.remove(current)
            visited.add(current)
            current.make_visited()
            item.draw()
            start_in.make_start()

            for item in current.algorithm_neighbours:
                if item not in visited:
                    temp_g = current.g + 1

                    new_path = False
                    if item in frontier:
                        if temp_g < item.g:
                            item.g = temp_g
                            new_path = True
                    else:
                        item.g = temp_g
                        new_path = True
                        frontier.append(item)
                        item.make_frontier()
                        item.draw()

                    if new_path:
                        item.h = heuristic(item, end_in, heuristic_in)
                        item.f = item.g + item.h
                        item.parent = current

        else:
            print("no path")
            break


path1 = []


def a_star_nopath(grid_in, start_in, end_in, heuristic_in):
    global path1
    visited = set()
    frontier = [start_in]

    print("searching")

    while True:
        if frontier:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            winner = 0

            for i in range(len(frontier)):
                if frontier[i].f < frontier[winner].f:
                    winner = i

            current = frontier[winner]

            # Draw the path in real time

            # draw_new(grid_in)
            path1 = []
            # Goal check
            if current == end_in:
                print("Done")

                path1 = []
                temp_goal = current
                path1.append(temp_goal)
                while temp_goal.parent:
                    path1.append(temp_goal.parent)
                    temp_goal = temp_goal.parent
                # return path
                break

            frontier.remove(current)
            visited.add(current)

            for item in current.algorithm_neighbours:
                if item not in visited:
                    temp_g = current.g + 1

                    new_path = False
                    if item in frontier:
                        if temp_g < item.g:
                            item.g = temp_g
                            new_path = True
                    else:
                        item.g = temp_g
                        new_path = True
                        frontier.append(item)

                    if new_path:
                        item.h = heuristic(item, end_in, heuristic_in)
                        item.f = item.g + item.h
                        item.parent = current

        else:
            print("no path")
            break


def chasealg(grid_in, start_in, heuristic_in):
    global end, start, path1

    while True:

        path = threading.Thread(target=a_star_nopath, args=(grid_in, start, end, heuristic_in))
        #path = multiprocessing.Process(target=a_star_nopath, args=(grid_in, start, end, heuristic_in))
        path.start()
        path.join()

        # for item in path1:
        if len(path1) > 5:
            for i in range(6):
                end.reset()
                end.draw()
                end = grid_in[path1[i].x_coord][path1[i].y_coord]
                end.make_end()
                end.draw()
                #pygame.display.update()
                time.sleep(0.1)
                if end == start:
                    break


    print("fin")
    end = None


def a_star_chase(grid_in, start_in, end_in, heuristic_in):
    global start, end
    # visited = set()
    frontier = [start_in]

    current = start_in

    while True:
        goal = start
        if current == goal:
            end = None
            break
        if frontier:
            current.reset()
            current.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            winner = 0

            for i in range(len(frontier)):
                if frontier[i].f < frontier[winner].f:
                    winner = i

            current = frontier[winner]
            frontier = []
            current.make_end()
            current.draw()

            # frontier.remove(current)
            # visited.add(current)

            for item in current.algorithm_neighbours:
                # if item not in visited:
                temp_g = current.g + 1

                new_path = False
                if item in frontier:
                    if temp_g < item.g:
                        item.g = temp_g
                        new_path = True
                else:
                    item.g = temp_g
                    new_path = True
                    frontier.append(item)

                if new_path:
                    item.h = heuristic(item, goal, heuristic_in)
                    item.f = item.g + item.h
                    item.parent = current

            # Goal check
            pygame.display.update()
            time.sleep(0.3)

            # current.make_end()
            # draw_new(grid_in)

            # return current


start = None
end = None


def main():
    global start, end
    running = True
    screen.fill(WHITE)
    grid = make_hex_node_grid_new()
    update_neighbours(grid)

    heuristic_choice = heuristic_setting

    while running:
        draw_new(grid)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # The user closed the window!
                running = False  # Stop running
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    start = move_hex(0, start)
                if event.key == pygame.K_s:
                    start = move_hex(3, start)
                if event.key == pygame.K_e:
                    start = move_hex(1, start)
                if event.key == pygame.K_d:
                    start = move_hex(2, start)
                if event.key == pygame.K_a:
                    start = move_hex(4, start)
                if event.key == pygame.K_q:
                    start = move_hex(5, start)

                if event.key == pygame.K_1:
                    heuristic_choice = 1
                    print("Euclidean")
                if event.key == pygame.K_2:
                    heuristic_choice = 2
                    print("Manhattan")

                if event.key == pygame.K_c:
                    reset_grid(grid)
                    start = None
                    end = None

                if event.key == pygame.K_KP_ENTER:
                    if start is not None and end is not None:
                        #chase = threading.Thread(target=chasealg, args=(grid, start, heuristic_choice))
                        # chase = multiprocessing.Process(target=chasealg, args=(grid, start, heuristic_choice))
                        #chase.start()
                        # print("run")
                        #a_star_chase(grid, end, start, heuristic_choice)
                        chase = threading.Thread(target=a_star_chase, args=(grid, end, start, heuristic_choice))
                        chase.start()

                if event.key == pygame.K_SPACE:
                    if start is not None and end is not None:
                        a_star(grid, start, end, heuristic_choice)

        if pygame.mouse.get_pressed()[0]:  # LEFT
            pos = pygame.mouse.get_pos()
            row, col = get_mouse_pos(pos)
            try:
                spot = grid[row][col]

                if start is None:
                    start = spot
                    start.make_start()
                elif spot != start and end is None:
                    end = spot
                    end.make_end()
                else:
                    if spot != start and spot != end:
                        spot.make_wall()

                update_single_neighbours(grid, spot)
            except TypeError:
                pass
            except IndexError:
                pass
            except UnboundLocalError:
                pass

        if pygame.mouse.get_pressed()[2]:  # RIGHT
            pos = pygame.mouse.get_pos()
            row, col = get_mouse_pos(pos)
            try:
                spot = grid[row][col]

                if spot == start:
                    start = None
                elif spot == end:
                    end = None

                spot.reset()
                update_single_neighbours(grid, spot)

            except TypeError:
                pass
            except IndexError:
                pass
            except UnboundLocalError:
                pass


main()
