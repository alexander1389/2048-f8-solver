import math
import numpy as np

from strategies.simple_strategy import SimpleStrategy


class ImprovedStrategy(SimpleStrategy):
    def __init__(self, debug=True):
        super().__init__(debug)

        self._init_weights()

        self._game_phase_weights = {
            'early': self._init_early_weights(),
            'mid': self._init_mid_weights(),
            'late': self._init_late_weights()
        }

        self._current_phase = 'mid'

    def _init_weights(self):
        self._weights = np.array([
            [65536, 32768, 16384, 8192],
            [512, 1024, 2048, 4096],
            [256, 128, 64, 32],
            [2, 4, 8, 16]
        ])

    def _init_early_weights(self):
        return np.array([
            [1.0, 0.8, 0.6, 0.4],
            [0.2, 0.3, 0.4, 0.5],
            [0.1, 0.15, 0.2, 0.25],
            [0.05, 0.1, 0.15, 0.2]
        ])

    def _init_mid_weights(self):
        return np.array([
            [10, 8, 7, 6.5],
            [0.5, 0.7, 1, 3],
            [-0.5, -1.5, -1.8, -2],
            [-3.8, -3.7, -3.5, -3]
        ])

    def _init_late_weights(self):
        return np.array([
            [100, 80, 60, 40],
            [5, 7, 10, 30],
            [-5, -15, -18, -20],
            [-38, -37, -35, -30]
        ])

    def get_game_phase(self, max_tile):
        if max_tile < 128:
            return 'early'
        elif max_tile < 1024:
            return 'mid'
        else:
            return 'late'

    def evaluate_position(self, board):
        max_tile = np.max(board)

        self._current_phase = self.get_game_phase(max_tile)
        phase_weights = self._game_phase_weights[self._current_phase]

        if max_tile >= 4096:
            return 1000000

        score = np.sum(board * self._weights) * 3.0
        score += np.sum(board * phase_weights) * 2.0
        score += self._advanced_monotonicity(board) * 2.0
        score += self._corner_max_tile_bonus(board) * 5.0

        free_cells = np.sum(board == 0)
        score += self._free_cells_bonus(free_cells, max_tile) * 150

        score += self._advanced_mergeability(board) * 75
        score -= self._strategic_penalty(board) * 25
        score += self._chain_bonus(board) * 40

        return score

    def _advanced_monotonicity(self, board):
        mono_score = 0
        snake_penalty = 0

        for i in range(4):
            if i % 2 == 0:
                for j in range(3):
                    current = math.log2(board[i, j]) if board[i, j] > 0 else 0
                    next_val = math.log2(board[i, j+1]) if board[i, j+1] > 0 else 0
                    if current >= next_val:
                        mono_score += 1
                    else:
                        snake_penalty += 1
            else:
                for j in range(3, 0, -1):
                    current = math.log2(board[i, j]) if board[i, j] > 0 else 0
                    next_val = math.log2(board[i, j-1]) if board[i, j-1] > 0 else 0
                    if current >= next_val:
                        mono_score += 1
                    else:
                        snake_penalty += 1

        for j in range(4):
            for i in range(3):
                current = math.log2(board[i, j]) if board[i, j] > 0 else 0
                next_val = math.log2(board[i+1, j]) if board[i+1, j] > 0 else 0
                if current >= next_val:
                    mono_score += 0.5

        return mono_score - snake_penalty * 0.5

    def _corner_max_tile_bonus(self, board):
        max_tile = np.max(board)
        corners = [(0, 0), (0, 3), (3, 0), (3, 3)]

        for i, j in corners:
            if board[i, j] == max_tile:
                return math.log2(max_tile) * 100 if max_tile > 0 else 0

        return 0

    def _free_cells_bonus(self, free_cells, max_tile):
        if free_cells == 0:
            return -1000

        base_bonus = math.log(free_cells + 1) * 10

        if self._current_phase == 'late':
            return base_bonus * 3
        elif self._current_phase == 'mid':
            return base_bonus * 2
        else:
            return base_bonus

    def _advanced_mergeability(self, board):
        merge_score = 0

        for i in range(4):
            for j in range(4):
                if board[i, j] == 0:
                    continue

                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < 4 and 0 <= nj < 4:
                        if board[ni, nj] == board[i, j]:
                            merge_score += math.log2(board[i, j]) * 2

                        elif board[ni, nj] == 0:
                            merge_score += math.log2(board[i, j]) * 0.5

        return merge_score

    def _strategic_penalty(self, board):
        penalty = 0

        corners = [(0, 0), (0, 3), (3, 0), (3, 3)]
        max_tile = np.max(board)

        for i, j in corners:
            if board[i, j] > 0 and board[i, j] < max_tile / 8:
                penalty += 2

        penalty += self._isolation_penalty(board) * 1.5

        return penalty

    def _chain_bonus(self, board):
        chain_bonus = 0

        for i in range(4):
            for j in range(3):
                if (
                    board[i, j] > 0 and board[i, j+1] > 0 and
                    math.log2(board[i, j+1]) - math.log2(board[i, j]) == 1
                ):
                    chain_bonus += board[i, j] * 0.1

        for j in range(4):
            for i in range(3):
                if (
                    board[i, j] > 0 and board[i+1, j] > 0 and
                    math.log2(board[i+1, j]) - math.log2(board[i, j]) == 1
                ):
                    chain_bonus += board[i, j] * 0.1

        return chain_bonus

    def find_best_move(self, board, next_tile=None, depth=None):
        free_cells = np.sum(board == 0)

        if depth is None:
            if self._current_phase == 'late' and free_cells <= 4:
                depth = 4
            elif self._current_phase == 'mid':
                depth = 3
            else:
                depth = 3

        return super().find_best_move(board, next_tile, depth)

    def find_aggressive_move(self, board):
        max_tile = np.max(board)

        if max_tile >= 1024:
            _, best_move = self.find_best_move(board, depth=3)
        else:
            _, best_move = self.find_best_move(board, depth=2)

        return best_move
