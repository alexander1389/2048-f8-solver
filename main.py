import argparse

from board_parser import BoardParser
from calibration import Calibrator
from solver import Solver
from strategies.simple_strategy import SimpleStrategy
from strategies.improved_strategy import ImprovedStrategy


def main():
    parser = argparse.ArgumentParser(description='Automatic Threes player')
    parser.add_argument(
        '-c', '--calibrate', action='store_true', help='Run calibration mode')
    parser.add_argument(
        '-p', '--parse', action='store_true', help='Run parsing mode (only recognize game state)')
    parser.add_argument(
        '-d', '--debug', action='store_true', help='Enable debug output')
    parser.add_argument(
        '-s', '--strategy', choices=['simple', 'improved', 'advanced', 'star', 'expectimax', 'd'], default='simple',
        help='Strategy to use (default: simple)')
    parser.add_argument(
        '-g', '--games', type=int, default=None,
        help='Maximum number of games to play (default: unlimited)')
    parser.add_argument(
        '-t', '--target', type=int, default=4096,
        help='Target tile value to reach (default: 4096)')
    parser.add_argument(
        '--pause-on-double-2048', action='store_true',
        help='Pause the game when two 2048 tiles appear for manual completion')
    parser.add_argument(
        '--profile', action='store_true',
        help='Enable performance profiling and statistics')

    args = parser.parse_args()

    if args.calibrate:
        Calibrator().calibrate()
    elif args.parse:
        try:
            BoardParser(debug=True, calibration_dir='./').parse_board_state()
        except Exception as e:
            print(f'Parsing error: {e}')
    else:
        if args.strategy == 'simple':
            strategy = SimpleStrategy(debug=args.debug, enable_profiling=args.profile)
        elif args.strategy == 'improved':
            strategy = ImprovedStrategy(debug=args.debug)

        solver = Solver(
            strategy=strategy,
            debug=args.debug,
            pause_on_double_2048=args.pause_on_double_2048,
            enable_profiling=args.profile
        )
        solver.play(target_score=args.target, max_games=args.games)


if __name__ == '__main__':
    main()
