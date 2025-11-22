import numpy as np

from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    def __init__(self, debug=True):
        self._debug = debug

    @abstractmethod
    def find_best_move(self, board, depth=2):
        pass

    @abstractmethod
    def evaluate_position(self, board):
        pass

    def can_merge(self, a, b):
        return a != 0 and a == b

    def simulate_move(self, board, direction):
        new_board = board.copy()
        changed = False

        if direction == 'left':
            for i in range(4):
                line = new_board[i].copy()
                new_line, line_changed = self._process_line_left(line)
                new_board[i] = new_line
                if line_changed:
                    changed = True

        elif direction == 'right':
            for i in range(4):
                line = new_board[i].copy()
                new_line, line_changed = self._process_line_right(line)
                new_board[i] = new_line
                if line_changed:
                    changed = True

        elif direction == 'up':
            for j in range(4):
                col = new_board[:, j].copy()
                new_col, col_changed = self._process_line_left(col)
                new_board[:, j] = new_col
                if col_changed:
                    changed = True

        elif direction == 'down':
            for j in range(4):
                col = new_board[:, j].copy()
                new_col, col_changed = self._process_line_right(col)
                new_board[:, j] = new_col
                if col_changed:
                    changed = True

        return new_board, changed

    def _process_line_left(self, line):
        original = line.copy()
        new_line = line.copy()
        moved = [False] * 4

        i = 0
        while i < 4:
            if new_line[i] == 0:
                for j in range(i + 1, 4):
                    if new_line[j] != 0:
                        new_line[i] = new_line[j]
                        new_line[j] = 0
                        moved[i] = True

                        if i > 0 and new_line[i] == new_line[i - 1] and not moved[i - 1]:
                            new_line[i - 1] *= 2
                            new_line[i] = 0
                            moved[i - 1] = True
                        else:
                            i += 1
                        break
                else:
                    i += 1
            else:
                if i > 0 and new_line[i] == new_line[i - 1] and not moved[i - 1]:
                    new_line[i - 1] *= 2
                    new_line[i] = 0
                    moved[i - 1] = True
                else:
                    i += 1

        changed = not np.array_equal(original, new_line)
        return new_line, changed

    def _process_line_right(self, line):
        original = line.copy()
        new_line = line.copy()
        moved = [False] * 4

        i = 3
        while i >= 0:
            if new_line[i] == 0:
                for j in range(i - 1, -1, -1):
                    if new_line[j] != 0:
                        new_line[i] = new_line[j]
                        new_line[j] = 0
                        moved[i] = True

                        if i < 3 and new_line[i] == new_line[i + 1] and not moved[i + 1]:
                            new_line[i + 1] *= 2
                            new_line[i] = 0
                            moved[i + 1] = True
                        else:
                            i -= 1
                        break
                else:
                    i -= 1
            else:
                if i < 3 and new_line[i] == new_line[i + 1] and not moved[i + 1]:
                    new_line[i + 1] *= 2
                    new_line[i] = 0
                    moved[i + 1] = True
                else:
                    i -= 1

        changed = not np.array_equal(original, new_line)
        return new_line, changed

    def is_game_over(self, board):
        if np.any(board == 0):
            return False

        for i in range(4):
            for j in range(3):
                if board[i, j] == board[i, j + 1]:
                    return False

                if board[j, i] == board[j + 1, i]:
                    return False

        return True
