# Pokemon Battle Simulator

A strategic turn-based battle simulator featuring an intelligent AI opponent powered by minimax algorithm with alpha-beta pruning.




## 📋 Overview

This project implements a functional Pokemon battle system where players face off against an AI opponent in strategic 3v3 battles. The game features authentic Pokemon mechanics including the comprehensive type system, speed-based turn order, and tactical move selection.

**Objective:** Strategically deploy your Pokemon and their moves to defeat all three opposing Pokemon before your team is knocked out.

## ✨ Features

### Core Mechanics

- **Type System**: Complete implementation of all 18 Pokemon types with authentic effectiveness calculations
  - Super effective, not very effective, and neutral damage interactions
  - Dual-type Pokemon support with simultaneous type matchup calculations
  - Type-independent moves (e.g., Water-type Pokemon can use Fire-type moves)

- **Speed-Based Combat**: Turn order determined by each Pokemon's speed stat
  - Faster Pokemon attack first
  - Random tie-breaker for equal speeds
  - Hidden opponent speed values for strategic depth

- **Team Selection**: Choose your preferred team from multiple randomly generated sets of 3 Pokemon

### Intelligent AI Opponent

Our AI uses **alpha-beta pruning with minimax tree search** to make strategic decisions based on a sophisticated heuristic that considers:

- **Type Effectiveness**: Prioritizes super effective moves
- **Threat Assessment**: Evaluates incoming damage potential
- **HP Management**: Weighs current and remaining HP ratios
- **Knockout Calculations**: Identifies finishing opportunities and defensive priorities
- **Risk Minimization**: Compares damage outputs across all available moves

## 🎮 Getting Started

### Prerequisites

- Python 3.8 or higher
- Required packages (install via `pip install -r requirements.txt`):
  - pygame
  - pandas
  - numpy

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Pobitro-B/CSL304-Project-Pokemon-Simulator
cd CSL304-Project-Pokemon-Simulator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
python main_ds.py
```

> **Important:** Run `main_ds.py`, not `main.py`

## 📁 Project Structure

```
pokemon-battle-simulator/
│
├── assets/              # Graphical resources
│   ├── sprites/         # Pokémon sprites
│   └── backgrounds/     # Battle backgrounds
│
├── data/                # Game data and statistics
│   └── bulbapedia_data.csv  # Pokémon stats, types, moves
│
├── core/                # Core game logic
│   ├── battle_state.py  # Battle state management
│   ├── pokemon.py       # Pokémon class and actions
│   ├── move.py          # Move mechanics and damage calculation
│   ├── type_effectiveness.py  # Type matchup system
│   └── ability.py       # Ability effects
│
├── ai/                  # AI opponent logic
│   ├── heuristic.py     # Move evaluation heuristic
│   ├── minimax_agent.py # Alpha-beta pruning implementation
│   └── mcts.py          # (Experimental) Monte Carlo tree search
│
├── engine/              # Game engine and UI
│   ├── game_loop.py     # Main game loop
│   ├── screens.py       # Screen rendering
│   └── input_handler.py # User input processing
│
└── main_ds.py           # Entry point
```

## 🎯 How to Play

1. **Team Selection**: Choose your preferred set of 3 Pokemon from the available options
2. **Battle Phase**: Take turns selecting moves for your active Pokémon
3. **Strategy**: Consider type effectiveness, remaining HP, and speed when making decisions
4. **Victory**: Defeat all three opposing Pokemon to win the match

### Battle Tips

- Super effective moves deal significantly more damage
- Pay attention to your Pokemon's remaining HP
- Faster Pokemon can finish off weakened opponents before they strike
- The AI is strategic—expect it to exploit type advantages

## 🛠️ Technical Highlights

- **Algorithm**: Minimax with alpha-beta pruning for efficient game tree search
- **Heuristic Design**: Multi-factor evaluation function balancing offense and defense
- **Data Management**: CSV-based Pokemon database with comprehensive statistics
- **Modular Architecture**: Clean separation of game logic, AI, and presentation layers

## 👥 Team

- **Ayush** (12340420)
- **Ajay** (12340580)
- **Kishor** (12341210)
- **Pobitro** (12341580)

## 🚀 Future Enhancements

Potential features for future development:
- Status conditions (paralysis, burn, freeze, etc.)
- Held items and abilities
- Weather effects and terrain
- Multi-turn moves
- Pokemon switching mid-battle
- Multiplayer support



## 🙏 Acknowledgments

- Pokemon data sourced from Bulbapedia
- Sprites and assets from the Pokemon franchise
- Inspired by the original Pokemon battle system

---

**Note**: This is an educational project created for learning purposes. 
