# 2048 AI Solver
An automated bot that plays the 2048 game for Fairchild Channel F emulator using computer vision and strategic decision-making. The bot implements multiple AI strategies to achieve high tile scores with consistent performance.

## Overview
This project combines several components to create an autonomous 2048 player:
- **Computer Vision** for board state recognition from the game screen
- **Game Simulation** for accurate move prediction based on 2048 mechanics
- **Multiple AI Strategies** with different optimization approaches
- **Performance Profiling** for analyzing bot efficiency
- **Validation System** to ensure simulation accuracy

## Components

### 1. Game Solver (`solver.py`)
The main orchestrator that controls the gameplay loop and integrates all components.

#### Key Features:
- **Multi-game Support**: Plays multiple games sequentially with statistics tracking
- **Adaptive Gameplay**: Adjusts strategy based on game phase (early, mid, late)
- **Validation System**: Optional simulation validation to ensure move prediction accuracy
- **Manual Mode**: Pause functionality when two 2048 tiles appear for manual completion
- **Comprehensive Logging**: Detailed game statistics, debug information, and screenshots

#### Game Loop Process:
1. **Board Capture**: Uses computer vision to get current game state
2. **Strategy Decision**: Evaluates position and selects optimal move
3. **Move Execution**: Sends keyboard commands to the game
4. **State Validation**: Compares actual vs predicted board state
5. **Progress Tracking**: Monitors achievements and game phases

### 2. Board Parser (`board_parser.py`)
Handles real-time game state recognition from the game screen.

#### Calibration System:
- **Region Definition**: Manually specify the game board region during calibration
- **Color Analysis**: Learns tile colors through user input
- **Grid Calculation**: Automatically determines tile positions and gaps
- **Data Persistence**: Saves calibration to `calibration_data.json`

#### Recognition Features:
- **Color-based Recognition**: Uses calibrated colors to identify tile values
- **Fast Processing**: Optimized for real-time gameplay (sub-second parsing)
- **Debug Visualization**: Saves intermediate images for calibration verification

### 3. AI Strategies
#### Base Strategy (`strategies/base_strategy.py`)
Provides the foundation with core game mechanics:
- Move simulation for all directions (left, right, up, down)
- Game-over detection algorithm
- Line processing logic for tile merging and movement

#### Simple Strategy (`strategies/simple_strategy.py`)
Basic but effective strategy focusing on:
- **Weighted Board Evaluation**: Prioritizes corner and edge positions
- **Monotonicity**: Encourages smooth tile gradients
- **Free Cell Bonus**: Rewards keeping empty spaces
- **Mergeability**: Encourages potential tile merges
- **Expectimax Algorithm**: 3-ply lookahead with probability consideration

#### Improved Strategy (`strategies/improved_strategy.py`)
Advanced strategy with phase-aware optimization:

##### Phase Detection:
- Early Game (<128 max tile): Focus on building foundation
- Mid Game (128-1024): Balance between growth and organization
- Late Game (>1024): Aggressive high-tile management

##### Advanced Evaluation Features:
- **Phase-specific Weights**: Different positional weights for each game phase
- **Corner Max Tile Bonus**: Extra reward for keeping largest tile in corner
- **Snake Pattern Optimization**: Encourages snake-like tile arrangement
- **Chain Bonus**: Rewards consecutive tile sequences (2-4-8-16...)
- **Strategic Penalties**: Discourages poor tile placements
- **Adaptive Search Depth**: Deeper lookahead in late game with few empty cells

### 4. Move Simulation Testing (`test_move_simulation.py`)
Validates that the game simulation matches actual 2048 mechanics.

#### Test Procedure:
1. **Autonomous Testing**: Runs predefined move sequences on the actual game
2. **State Comparison**: Compares simulated vs actual board states after each move
3. **Accuracy Calculation**: Measures simulation reliability percentage
4. **Visual Reporting**: Generates detailed comparison logs with visual representations

### 5. Calibration System (`calibration.py`)
Interactive tool for setting up the board recognition system.

#### Calibration Steps:
1. **Full Screen Capture**: Takes screenshot of entire display with game
2. **Region Selection**: Manual specification of game board coordinates
3. **Tile Size Definition**: Input tile dimensions for grid calculation
4. **Color Sampling**: User-assisted tile color learning
5. **Verification**: Test recognition on current board state
6. **Data Persistence**: Saves calibration to `calibration_data.json`

#### Important Calibration Notes for Fairchild Channel F Emulator:
**Sample Coordinates (MacBook Pro):**
- **Board Region**: `95 251 1806 1874`
- **Tile Width**: `383`
- **Tile Height**: `383`

**Important**: These coordinates are specific to my MacBook Pro setup. On other systems and screen configurations, you MUST manually determine the correct coordinates during calibration.

#### Calibration Tips:
1. **Consistent Window Placement**: Always position the emulator window in the same location
2. **Full Screen Reference**: Use the full screenshot to identify your specific coordinates
3. **Coordinate Format**: Use `left top right bottom` format (pixels from top-left corner)
4. **Verification**: Test parsing after calibration to ensure accurate recognition
5. **Multiple Displays**: If using multiple monitors, ensure the emulator is on the primary display

#### Finding Your Coordinates:
1. Run `python main.py --calibrate`
2. Examine the saved `01_full_screen.png`
3. Use an image editor or screenshot tool to find:
   - **Board**: The entire 4x4 grid of tiles
   - **Tile Width/Height**: Linear dimensions of a tile
4. Enter the coordinates when prompted during calibration

### 6. Performance Profiler (`profiler.py`)
Monitors and reports performance metrics for optimization.

#### Tracked Metrics:
- **Timing Statistics**: Move selection, board parsing, execution times
- **Game Statistics**: Final scores, move counts, success rates
- **Memory Usage**: Strategy evaluation counts and cache performance
- **Custom Metrics**: User-defined performance indicators

## Installation and Setup

### Prerequisites:
- Fairchild Channel F emulator with [2048-F8 game](https://arlagames.itch.io/2048-for-fairchild-channel-f)
- Python 3.7+ with required dependencies

### Initial Setup:
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -f requirements.txt

# Run calibration (ensure 2048 game is visible on screen)
python main.py --calibrate

# Test board recognition
python main.py --parse

# Validate move simulation
python test_move_simulation.py
```

### Usage
#### Basic Gameplay:
```bash
# Simple strategy with debug output
python main.py --strategy simple --debug

# Improved strategy targeting 2048 tile
python main.py --strategy improved --target 2048

# Play multiple games with profiling
python main.py --strategy improved --games 10 --profile
```

#### Advanced Options:
```bash
# Enable pause on double 2048 for manual completion
python main.py --pause-on-double-2048 --target 4096

# Deep search with improved strategy
python main.py --strategy improved --target 8192 --debug

# Performance-optimized mode (minimal output)
python main.py --strategy simple --target 1024
```

### Command Line Arguments:
- `-c, --calibrate`: Run calibration mode to set up board recognition
- `-p, --parse`: Test board recognition only without playing
- `-d, --debug`: Enable detailed debug output and logging
- `-s, --strategy`: AI strategy (simple or improved) - default: simple
- `-t, --target`: Target tile value to achieve - default: 4096
- `-g, --games`: Maximum number of games to play - default: unlimited
- `--pause-on-double-2048`: Pause when two 2048 tiles appear for manual completion
- `--profile`: Enable performance profiling and statistics

## Performance

### Current Capabilities:
- **High Tile Achievement**: Consistently reaches 2048, often achieves 4096+
- **Fast Execution**: ~0.1-0.3 seconds per move decision
- **High Accuracy**: >99% move simulation accuracy
- **Adaptive Intelligence**: Adjusts strategy based on game phase
- **Error Resilience**: Recovers from recognition failures and game glitches

### Strategy Comparison:
- **Simple Strategy**: Faster, more consistent for lower targets (≤2048)
- **Improved Strategy**: Higher peak performance, better for ambitious targets (≥4096)

### Optimization Features:
- **Phase-aware Evaluation**: Different optimization criteria for early/mid/late game
- **Adaptive Search Depth**: Deeper lookahead when board is more constrained
- **Aggressive Mode**: Special logic for high-pressure situations with few empty cells
- **Cached Evaluations**: Memoization of position evaluations for speed

## Technical Implementation
### Game Mechanics:
- **Accurate Simulation**: Correctly models 2048 merging rules and movement
- **Probability Handling**: Accounts for 90% 2-tile / 10% 4-tile spawn probabilities
- **Game State Detection**: Reliable recognition of game-over conditions

### Computer Vision:
- **Robust Recognition**: Color-based matching with distance thresholds
- **Scale Adaptation**: Handles different screen resolutions and DPI settings
- **Error Recovery**: Fallback strategies for recognition failures

### AI Algorithms:
- **Expectimax Search**: Probability-weighted lookahead for optimal move selection
- **Heuristic Evaluation**: Multi-factor position scoring combining:
    - Monotonicity patterns
    - Corner positioning
    - Empty space management
    - Merge potential
    - Tile organization

## Future Improvements
### Planned Enhancements:
- **Neural Network Strategy**: ML-based evaluation function trained on expert games
- **Monte Carlo Tree Search**: Advanced search algorithm for deeper lookahead
- **Opening Book**: Pre-calculated optimal moves for common early game positions
- **Parallel Processing**: Multi-threaded move evaluation for faster decision making
- **Cloud Optimization**: Shared learning between multiple bot instances

### Research Directions:
- Reinforcement learning for strategy optimization
- Pattern recognition for common high-score board configurations
- Adaptive difficulty scaling for different game variants

## Contributing
Contributions are welcome in these areas:
- Developing new AI strategies with innovative evaluation functions
- Optimizing performance for higher tile achievement (8192+)
- Enhancing computer vision reliability
- Improving calibration process for easier setup
- Creating visualization tools for strategy analysis

## License
This project is open source and available for educational and research purposes.
