from tkinter import Tk, BOTH, Canvas
import time
import random


class Window:
    def __init__(self, width, height):
        self.__root = Tk()
        self.__root.title = "Maze Solver"
        self.__root.protocol("WM_DELETE_WINDOW", self.close)
        self.canvas = Canvas()
        self.canvas.pack()
        self.running = False

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.running = True

        while self.running:
            self.redraw()

    def close(self):
        self.running = False

    def draw_line(self, line, fill_color):
        line.draw(self.canvas, fill_color)


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line:
    def __init__(self, point1: Point, point2: Point):
        self.point1 = point1
        self.point2 = point2

    def draw(self, canvas: Canvas, fill_color: str):
        canvas.create_line(
            self.point1.x, self.point1.y, self.point2.x, self.point2.y, fill=fill_color, width=2
        )


class Cell:
    def __init__(
            self, has_left_wall=False, has_right_wall=False, has_top_wall=False, has_bottom_wall=False,
            x1=0, x2=0, y1=0, y2=0, win=None
    ):
        self.has_left_wall = has_left_wall
        self.has_right_wall = has_right_wall
        self.has_top_wall = has_top_wall
        self.has_bottom_wall = has_bottom_wall
        self._x1 = x1
        self._x2 = x2
        self._y1 = y1
        self._y2 = y2
        self._win = win
        self._visited = False

    def draw(self):
        point1 = Point(self._x1, self._y1)
        point2 = Point(self._x1, self._y2)
        line = Line(point1, point2)
        if self.has_left_wall and self._win:
            self._win.draw_line(line, "black")
        elif not self.has_left_wall and self._win:
            self._win.draw_line(line, "#d9d9d9")

        point1 = Point(self._x2, self._y1)
        point2 = Point(self._x2, self._y2)
        line = Line(point1, point2)
        if self.has_right_wall and self._win:
            self._win.draw_line(line, "black")
        elif not self.has_right_wall and self._win:
            self._win.draw_line(line, "#d9d9d9")

        point1 = Point(self._x1, self._y1)
        point2 = Point(self._x2, self._y1)
        line = Line(point1, point2)
        if self.has_top_wall and self._win:
            self._win.draw_line(line, "black")
        elif not self.has_top_wall and self._win:
            self._win.draw_line(line, "#d9d9d9")

        point1 = Point(self._x1, self._y2)
        point2 = Point(self._x2, self._y2)
        line = Line(point1, point2)
        if self.has_bottom_wall and self._win:
            self._win.draw_line(line, "black")
        elif not self.has_bottom_wall and self._win:
            self._win.draw_line(line, "#d9d9d9")

    def draw_move(self, to_cell, undo=False):
        from_mid_x = (self._x1 + self._x2) // 2
        from_mid_y = (self._y1 + self._y2) // 2
        point1 = Point(from_mid_x, from_mid_y)

        to_mid_x = (to_cell._x1 + to_cell._x2) // 2
        to_mid_y = (to_cell._y1 + to_cell._y2) // 2
        point2 = Point(to_mid_x, to_mid_y)

        line = Line(point1, point2)
        color = "gray" if undo else "red"
        self._win.draw_line(line, color)


class Maze:
    def __init__(self, x1, y1, num_rows, num_cols, cell_size_x, cell_size_y, win=None, seed=None):
        if seed is not None:
            random.seed(seed)
        self.x1 = x1
        self.y1 = y1
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self.win = win
        self._cells = []
        self._create_cells()

    def _create_cells(self):
        self._cells = [[Cell() for j in range(self.num_cols)] for i in range(self.num_rows)]
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self._draw_cell(i, j)

        self._break_entrance_and_exit()
        self._break_walls(0, 0)
        self._reset_cells_visited()

    def _draw_cell(self, i, j):
        cell_x1 = j * self.cell_size_x + self.x1
        cell_x2 = cell_x1 + self.cell_size_x
        cell_y1 = i * self.cell_size_y + self.y1
        cell_y2 = cell_y1 + self.cell_size_y

        cell = self._cells[i][j]
        cell.has_left_wall=True
        cell.has_right_wall=True
        cell.has_top_wall=True
        cell.has_bottom_wall=True
        cell._x1 = cell_x1
        cell._x2 = cell_x2
        cell._y1 = cell_y1
        cell._y2 = cell_y2
        cell._win = self.win

        if self.win:
            cell.draw()
            self._animate()

    def _animate(self):
        self.win.redraw()
        time.sleep(0.05)

    def _break_entrance_and_exit(self):
        entry = self._cells[0][0]
        exit = self._cells[-1][-1]

        entry.has_left_wall = False
        entry.draw()
        exit.has_right_wall = False
        exit.draw()

    def _break_walls(self, i, j):
        cell = self._cells[i][j]
        cell._visited = True
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        def valid(i, j):
            return 0 <= i < len(self._cells) and 0 <= j < len(self._cells[0])

        while True:
            possible_directions = []
            for x, y in directions:
                next_i, next_j = i + x, y + j
                if valid(next_i, next_j):
                    neighbor = self._cells[next_i][next_j]
                    if not neighbor._visited:
                        possible_directions.append((next_i, next_j))
            if not possible_directions:
                cell.draw()
                return
            neighbor_i, neighbor_j = possible_directions[int(random.random() * 10) % len(possible_directions)]
            neighbor = self._cells[neighbor_i][neighbor_j]

            if j < neighbor_j:
                cell.has_right_wall = False
                neighbor.has_left_wall = False
            if i < neighbor_i:
                cell.has_bottom_wall = False
                neighbor.has_top_wall = False
            if j > neighbor_j:
                cell.has_left_wall = False
                neighbor.has_right_wall = False
            if i > neighbor_i:
                cell.has_top_wall = False
                neighbor.has_bottom_wall = False

            self._break_walls(neighbor_i, neighbor_j)

    def _reset_cells_visited(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self._cells[i][j].visited = False

    def solve(self):
        return self._solve_r(0, 0)

    def _solve_r(self, i, j):
        self._animate()
        cell = self._cells[i][j]
        cell.visited = True
        if i == self.num_rows - 1 and j == self.num_cols - 1:
            return True

        def valid(i, j):
            return 0 <= i < self.num_rows and 0 <= j < self.num_cols

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for x, y in directions:
            neighbor_i, neighbor_j = i + x, j + y
            if valid(neighbor_i, neighbor_j) and self._cells[neighbor_i][neighbor_j].visited is False:
                neighbor = self._cells[neighbor_i][neighbor_j]
                if j < neighbor_j and not cell.has_right_wall:
                    cell.draw_move(neighbor)
                    if self._solve_r(neighbor_i, neighbor_j):
                        return True
                    cell.draw_move(neighbor, undo=True)
                if i < neighbor_i and not cell.has_bottom_wall:
                    cell.draw_move(neighbor)
                    if self._solve_r(neighbor_i, neighbor_j):
                        return True
                    cell.draw_move(neighbor, undo=True)
                if j > neighbor_j and not cell.has_left_wall:
                    cell.draw_move(neighbor)
                    if self._solve_r(neighbor_i, neighbor_j):
                        return True
                    cell.draw_move(neighbor, undo=True)
                if i > neighbor_i and not cell.has_top_wall:
                    cell.draw_move(neighbor)
                    if self._solve_r(neighbor_i, neighbor_j):
                        return True
                    cell.draw_move(neighbor, undo=True)
        return False


def main():
    win = Window(800, 600)
    m1 = Maze(15, 15, 10, 10, 24, 24, win)
    m1.solve()
    win.wait_for_close()


main()
