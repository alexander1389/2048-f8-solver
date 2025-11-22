import numpy as np
import os
import pyautogui
import time

from datetime import datetime
from board_parser import BoardParser
from profiler import Profiler
from strategies.simple_strategy import SimpleStrategy


class Solver:
    def __init__(
        self,
        strategy=None,
        debug=True,
        log_dir='./logs',
        screenshots_dir='./screenshots',
        validate_simulation=False,
        pause_on_double_2048=False,
        enable_profiling=True
    ):
        self._debug = debug
        self._board_parser = BoardParser(debug=debug, calibration_dir='./')

        self._strategy = strategy or SimpleStrategy(debug=self._debug)

        self._validate_simulation = validate_simulation
        self._pause_on_double_2048 = pause_on_double_2048
        self._enable_profiling = enable_profiling

        self._profiler = Profiler(enabled=enable_profiling)

        self._move_count = 0
        self._consecutive_failures = 0
        self._max_tile_reached = 0
        self._consecutive_no_change = 0

        self._screenshots_dir = screenshots_dir
        self._log_dir = log_dir
        self._log_file = None

        self.setup_directories()
        self.setup_logging()

    def has_double_2048(self, board):
        return np.sum(board == 2048) >= 2

    def wait_for_manual_completion(self, board):
        print('\n' + '='*60)
        print('🎯 TWO 2048 TILES DETECTED!')
        print('='*60)
        print('Program paused.')
        print('You can complete the game in manual mode.')
        print('Press Ctrl+C to resume automatic game')
        print('or close the program after manual completion.')
        print('='*60)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        state_file = os.path.join(self._log_dir, f'double_2048_state_{timestamp}.txt')

        with open(state_file, 'w', encoding='utf-8') as f:
            f.write('DOUBLE 2048 DETECTED - MANUAL COMPLETION MODE\n')
            f.write('='*50 + '\n')
            f.write(f'Timestamp: {datetime.now()}\n')
            f.write(f'Move count: {self._move_count}\n')
            f.write('Current board state:\n')
            self._write_board_to_file(f, board)

        print(f'Current state saved to: {state_file}')
        print('Current board:')
        print(self.print_compact_board(board))

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print('\nResuming automatic game...')

    def _compare(self, real_board, sim_board):
        modified_sim = sim_board.copy()

        for i in range(4):
            for j in range(4):
                if real_board[i, j] != 0 and sim_board[i, j] == 0:
                    modified_sim[i, j] = real_board[i, j]

        return np.array_equal(real_board, modified_sim)

    def validate_simulation(self, board_before, direction, board_after_actual):
        print(f'{direction=}')
        try:
            board_after_simulated, _ = self._strategy.simulate_move(board_before, direction)

            if not self._compare(board_after_actual, board_after_simulated):
                print('\n' + '='*60)
                print('🚨 SIMULATION VALIDATION FAILED! 🚨')
                print(f'Direction: {direction}')
                print(f'Move count: {self._move_count}')
                print('='*60)

                print('\nBEFORE move:')
                print(self.print_compact_board(board_before))

                print('\nACTUAL result:')
                print(self.print_compact_board(board_after_actual))

                print('\nSIMULATED result:')
                print(self.print_compact_board(board_after_simulated))

                print('\nDIFFERENCES:')
                for i in range(4):
                    for j in range(4):
                        actual = board_after_actual[i, j]
                        simulated = board_after_simulated[i, j]
                        if actual != simulated:
                            print(f'  Position ({i},{j}): Actual={actual}, Simulated={simulated}')

                print('='*60)

                self.save_validation_failure(board_before, direction, board_after_actual, board_after_simulated)

                raise SimulationValidationError(f'Simulation mismatch for direction {direction}')

            if self._debug:
                print(f'✅ Simulation validated for {direction}')

        except Exception as e:
            print(f'Error during simulation validation: {e}')
            raise

    def save_validation_failure(self, board_before, direction, board_after_actual, board_after_simulated):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self._log_dir, f'simulation_failure_{timestamp}.txt')

            with open(filename, 'w', encoding='utf-8') as f:
                f.write('SIMULATION VALIDATION FAILURE REPORT\n')
                f.write('=' * 50 + '\n')
                f.write(f'Timestamp: {datetime.now()}\n')
                f.write(f'Move count: {self._move_count}\n')
                f.write(f'Direction: {direction}\n\n')

                f.write('BEFORE move:\n')
                self._write_board_to_file(f, board_before)

                f.write('\nACTUAL result:\n')
                self._write_board_to_file(f, board_after_actual)

                f.write('\nSIMULATED result:\n')
                self._write_board_to_file(f, board_after_simulated)

                f.write('\nDIFFERENCES:\n')
                for i in range(4):
                    for j in range(4):
                        actual = board_after_actual[i, j]
                        simulated = board_after_simulated[i, j]
                        if actual != simulated:
                            f.write(f'  Position ({i},{j}): Actual={actual}, Simulated={simulated}\n')

            print(f'Validation failure saved to: {filename}')

        except Exception as e:
            print(f'Failed to save validation report: {e}')

    def _write_board_to_file(self, file, board):
        for i in range(4):
            row = [f'{cell:4}' if cell != 0 else '   .' for cell in board[i]]
            file.write(' '.join(row) + '\n')

    def setup_directories(self):
        for directory in [self._log_dir, self._screenshots_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def setup_logging(self):
        if not os.path.exists(self._log_dir):
            os.makedirs(self._log_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f'2048_game_{timestamp}.log'
        self._log_file = open(os.path.join(self._log_dir, log_filename), 'w', encoding='utf-8')

        self.log('=== 2048-F8 SOLVER LOG ===')
        self.log(f'Started at: {datetime.now()}')
        self.log(f'Strategy: {self._strategy.__class__.__name__}')

    def log(self, message, console=True, level='WARNING'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f'[{timestamp}] {level}: {message}'

        if self._log_file:
            self._log_file.write(f'{log_message}\n')
            self._log_file.flush()

        if console and self._debug and level != 'DEBUG':
            print(log_message)

    def close_logging(self):
        if self._log_file:
            self.log('=== GAME FINISHED ===')
            self.log(f'Finished at: {datetime.now()}')
            self._log_file.close()

    def save_final_screenshot(self):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = os.path.join(self._screenshots_dir, f'game_over_{timestamp}.png')

            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)

            self.log(f'Final screenshot saved: {screenshot_path}')

            return True

        except Exception as e:
            self.log(f'Failed to save final screenshot: {e}', level='ERROR')
            return False

    def restart_game(self):
        self.log('Restarting game...')

        try:
            pyautogui.keyDown('enter')
            time.sleep(0.1)
            pyautogui.keyUp('enter')

            time.sleep(1)

            pyautogui.keyDown('z')
            time.sleep(0.1)
            pyautogui.keyUp('z')

            time.sleep(1)

            pyautogui.keyDown('enter')
            time.sleep(0.1)
            pyautogui.keyUp('enter')

            time.sleep(1)

            pyautogui.keyDown('down')
            time.sleep(0.1)
            pyautogui.keyUp('down')

            time.sleep(2.0)

            self.log('Game restarted successfully')

            return True

        except Exception as e:
            self.log(f'Failed to restart game: {e}', level='ERROR')
            return False

    def reset_game_stats(self):
        self._move_count = 0
        self._consecutive_failures = 0
        self._max_tile_reached = 0
        self._consecutive_no_change = 0

    def get_game_phase(self, max_tile):
        if hasattr(self._strategy, 'get_game_phase'):
            return self._strategy.get_game_phase(max_tile)
        return 'mid'

    def get_board_state(self):
        board, _ = self._board_parser.parse_board()
        return board

    def make_move(self, direction):
        self.log(f'Executing: {direction}', level='INFO')

        for _ in range(1):
            pyautogui.keyDown(direction)
            time.sleep(0.005)
            pyautogui.keyUp(direction)
            time.sleep(0.005)

        self._move_count += 1

        time.sleep(0.01)

    def has_reached_target(self, board, target=384):
        reached = np.any(board >= target)
        if reached:
            self.log(f'🎉 TARGET {target} REACHED! 🎉')
        return reached

    def is_game_over(self, board):
        return self._strategy.is_game_over(board)

    def print_compact_board(self, board):
        board_str = ''
        for i in range(4):
            row = [f'{cell:2}' if cell > 0 else ' .' for cell in board[i]]
            board_str += ' '.join(row) + '\n'
        return board_str.strip()

    def play_single_game(self, target_score=384):
        if self._enable_profiling:
            self._profiler.start_game()

        self.log(f'Starting new game - target: {target_score}')
        if self._pause_on_double_2048:
            self.log('Pause mode for two 2048 tiles: ENABLED')
        self._board_parser.countdown_timer(3)

        max_failures = 5
        aggressive_mode = False

        try:
            while True:
                try:
                    if self._enable_profiling:
                        self._profiler.start_timer('board_parsing')

                    board = self.get_board_state()

                    if self._enable_profiling:
                        self._profiler.stop_timer('board_parsing')

                    if self._pause_on_double_2048 and self.has_double_2048(board):
                        self.log('TWO 2048 TILES DETECTED! Activating manual completion mode')
                        self.wait_for_manual_completion(board)
                        self._pause_on_double_2048 = False
                        self.log('Resuming automatic game...')

                    current_max = np.max(board)
                    free_cells = np.sum(board == 0)

                    phase = self.get_game_phase(current_max)
                    self.log(
                        f'Move {self._move_count+1:2d} | Max: {current_max:3d} | Free: {free_cells} '
                        f'| Phase: {phase}'
                    )

                    if self._debug:
                        print(self.print_compact_board(board))
                        print()

                    if self.has_reached_target(board, target_score):
                        break

                    if self.is_game_over(board):
                        self.log('GAME OVER - NO MOVES LEFT')
                        break

                    if free_cells <= 3 and current_max >= 48:
                        aggressive_mode = True
                        self.log('ACTIVATING AGGRESSIVE MODE - few free cells and high tiles')

                    if self._enable_profiling:
                        self._profiler.start_timer('move_selection')

                    if aggressive_mode and hasattr(self._strategy, 'find_aggressive_move'):
                        aggressive_dir = self._strategy.find_aggressive_move(board)
                        direction = aggressive_dir
                        aggressive_mode = False
                    else:
                        depth = 3 if free_cells <= 4 else 2
                        _, best_direction = self._strategy.find_best_move(board, depth=depth)
                        direction = best_direction

                    if self._enable_profiling:
                        self._profiler.stop_timer('move_selection')
                        self._profiler.record_value('moves_per_game', 1)

                    if self._enable_profiling:
                        self._profiler.start_timer('move_execution')

                    self.make_move(direction)

                    if self._enable_profiling:
                        self._profiler.stop_timer('move_execution')

                    if self._enable_profiling:
                        self._profiler.start_timer('board_validation')

                    new_board = self.get_board_state()
                    if self._validate_simulation:
                        self.validate_simulation(board, direction, new_board)

                    if self._enable_profiling:
                        self._profiler.stop_timer('board_validation')

                    self._consecutive_failures = 0

                except SimulationValidationError:
                    self.log('Game stopped due to simulation validation error', level='ERROR')
                    break

                except Exception as e:
                    self.log(f'Error: {e}', level='ERROR')
                    self._consecutive_failures += 1
                    if self._consecutive_failures >= max_failures:
                        self.log('Too many consecutive errors, stopping')
                        break
                    time.sleep(1)

        finally:
            final_score = np.max(board)
            final_stats = f'Game finished - Moves: {self._move_count}, Max tile: {final_score}'

            self.log(final_stats)
            self.save_final_screenshot()

            if self._enable_profiling:
                self._profiler.end_game()
                self._profiler.record_value('final_score', final_score)
                self._profiler.record_value('moves_count', self._move_count)
                self._profiler.print_report(log_func=self.log)

            return np.max(board), self._move_count

    def play(self, target_score=384, max_games=None):
        game_count = 0
        best_score = 0
        total_moves = 0

        if self._enable_profiling:
            self._profiler.start_timer('total_session')

        try:
            while max_games is None or game_count < max_games:
                game_count += 1
                self.log(f'=== STARTING GAME {game_count} ===')

                max_tile, moves = self.play_single_game(target_score)

                if max_tile > best_score:
                    best_score = max_tile
                total_moves += moves

                self.log(f'Game {game_count} completed: Max tile = {max_tile}, Moves = {moves}')
                self.log(f'Best score so far: {best_score}')

                self.restart_game()
                self.reset_game_stats()

                time.sleep(1)

        except KeyboardInterrupt:
            self.log('Game interrupted by user')

        finally:
            if self._enable_profiling:
                self._profiler.stop_timer('total_session')
                self._profiler.print_report(log_func=self.log)

            if game_count > 0:
                avg_moves = total_moves / game_count
                self.log('=== FINAL STATISTICS ===')
                self.log(f'Games played: {game_count}')
                self.log(f'Best score: {best_score}')
                self.log(f'Average moves per game: {avg_moves:.1f}')

            self.close_logging()


class SimulationValidationError(Exception):
    pass
