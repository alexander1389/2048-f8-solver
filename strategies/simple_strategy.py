import math
import numpy as np

from strategies.base_strategy import BaseStrategy


class SimpleStrategy(BaseStrategy):
    def __init__(self, debug=True):
        super().__init__(debug)

        self._weights = None
        self._init_weights()

    def _init_weights(self):
        self._weights = np.array([
            [10, 8, 7, 6.5],
            [0.5, 0.7, 1, 3],
            [-0.5, -1.5, -1.8, -2],
            [-3.8, -3.7, -3.5, -3]
        ])

    def evaluate_position(self, board):
        if np.max(board) >= 4096:
            return 1000000

        score = np.sum(board * self._weights) * 2.0
        score += self._monotonicity(board) * 1.5

        free_cells = np.sum(board == 0)
        if free_cells == 0:
            score -= 10000
        else:
            score += math.log(free_cells) * 100

        score += self._mergeability(board) * 50
        score -= self._isolation_penalty(board) * 10

        return score

    def _monotonicity(self, board):
        mono = 0

        for i in range(4):
            for j in range(3):
                current = math.log2(board[i, j]) if board[i, j] > 0 else 0
                next_val = math.log2(board[i, j+1]) if board[i, j+1] > 0 else 0
                if current > next_val:
                    mono += 1
                elif current < next_val:
                    mono -= 1

        for j in range(4):
            for i in range(3):
                current = math.log2(board[i, j]) if board[i, j] > 0 else 0
                next_val = math.log2(board[i+1, j]) if board[i+1, j] > 0 else 0
                if current > next_val:
                    mono += 1
                elif current < next_val:
                    mono -= 1

        return abs(mono)

    def _mergeability(self, board):
        merges = 0

        for i in range(4):
            for j in range(4):
                if board[i, j] == 0:
                    continue

                for dx, dy in [(0, 1), (1, 0)]:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < 4 and 0 <= nj < 4 and board[ni, nj] == board[i, j]:
                        merges += 1

        return merges

    def _isolation_penalty(self, board):
        penalty = 0

        for i in range(4):
            for j in range(4):
                if board[i, j] > 0:
                    has_similar_neighbor = False
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < 4 and 0 <= nj < 4:
                            if board[ni, nj] == board[i, j]:
                                has_similar_neighbor = True
                                break

                    if not has_similar_neighbor and board[i, j] >= 8:
                        penalty += 1

        return penalty

    def simulate_move(self, board, direction):
        return super().simulate_move(board, direction)

    def find_best_move(self, board, next_tile=None, depth=3):
        best_score = -float('inf')
        best_move = 'left'

        moves = ['left', 'right', 'up', 'down']

        for move in moves:
            new_board, moved = self.simulate_move(board, move)
            if not moved:
                continue

            expected_score = self._expectimax(new_board, depth-1, False)

            if expected_score > best_score:
                best_score = expected_score
                best_move = move

        return best_score, best_move

    def _expectimax(self, board, depth, is_maximizing):
        if depth == 0:
            return self.evaluate_position(board)

        if is_maximizing:
            max_score = -float('inf')

            for move in ['left', 'right', 'up', 'down']:
                new_board, moved = self.simulate_move(board, move)
                if moved:
                    score = self._expectimax(new_board, depth-1, False)
                    max_score = max(max_score, score)

            return max_score if max_score != -float('inf') else self.evaluate_position(board)

        else:
            empty_cells = self._get_empty_cells(board)

            if not empty_cells:
                return self.evaluate_position(board)

            expected_score = 0
            total_prob = 0

            evaluated_cells = min(3, len(empty_cells))

            for i in range(evaluated_cells):
                cell = empty_cells[i]

                for tile_value, prob in [(2, 0.9), (4, 0.1)]:
                    new_board = board.copy()
                    new_board[cell[0], cell[1]] = tile_value

                    score = self._expectimax(new_board, depth-1, True)
                    expected_score += score * prob
                    total_prob += prob

            return expected_score / total_prob if total_prob > 0 else self.evaluate_position(board)

    def _get_empty_cells(self, board):
        empty_cells = [(i, j) for i in range(4) for j in range(4) if board[i, j] == 0]
        empty_cells.sort(key=lambda pos: (min(pos[0], 3-pos[0]) + min(pos[1], 3-pos[1])))

        return empty_cells

    def _get_corner_weights(self, board):
        weights = np.array([
            [4, 3, 2, 1],
            [3, 2, 1, 0],
            [2, 1, 0, -1],
            [1, 0, -1, -2]
        ])

        return np.sum(board * weights)

    def find_aggressive_move(self, board):
        _, best_move = self.find_best_move(board, depth=2)
        return best_move
