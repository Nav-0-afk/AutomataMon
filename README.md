# AutomataMon: Finite State Battle Engine

AutomataMon is a turn-based Python and Pygame-powered Pokémon battle simulator where core game mechanics and combat state transitions are strictly governed by a formal 9-state Deterministic Finite Automaton (DFA) backend rather than arbitrary conditional flags. By parsing JFLAP XML automaton files directly into runtime state-transition tables, this project bridges formal language theory with classic 2D game architecture.

---

## Table of Contents

1. [Key Features](#key-features)
2. [Project Architecture](#project-architecture)
3. [Automaton Specification](#automaton-specification)
4. [Controls](#controls)
5. [Getting Started](#getting-started)
6. [License](#license)

---

## Key Features

* **Formal DFA Backend**: Combat states, validity checks (`can_attack`), and status affliction routing are dynamically evaluated via a 9-state Deterministic Finite Automaton parsed directly from JFLAP (`States.jff`).
* **State-Aware CPU Artificial Intelligence**: The opponent evaluates board variables mathematically—prioritizing recovery items when health drops below critical thresholds, applying status conditions strategically, and executing optimal offensive lines.
* **Extended Status Mechanics**:
  * **Sleep (`SLP`)**: Disables combat actions for a randomized duration of 1 to 3 turns.
  * **Burn (`BRN`)**: Drains 1/16th of maximum hit points per turn and halves physical attack output. Fire-type Pokémon (such as Charmander) possess absolute immunity.
  * **Poison (`PSN`)**: Drains 1/8th of maximum hit points per turn.
  * **Paralysis (`PAR`)**: Incorporates a 25% probability check to transition the automaton into a full-paralysis stun-lock state (`q7` to `q8`).
  * **Rest (`r`)**: Cleanses non-volatile status conditions, forces a temporary sleep state, and restores hit points.
* **Pixel-Art Rendering & Flipbook Animations**: Supports grid-sliced spritesheets (5x3, 4x3) for dynamic move animations, synchronized to targeted bounding boxes and throttled frame rates mimicking retro handheld RPGs.
* **Typewriter Combat Log**: A text rendering engine that outputs log strings character-by-character with automatic pixel-boundary word wrapping across UI panels.

---

## Project Architecture

```text
MiniProject/
│
├── assets/
│   ├── animations/        # Move spritesheets (fire, electric, grass, etc.)
│   ├── fonts/             # Custom TrueType fonts (power clear bold.ttf)
│   ├── sprites/           # Pokémon front and back battlers (.gif / .png)
│   └── ui/                # Backgrounds, selection arrows, and status badges (statuses_2.png)
│
├── engine/
│   ├── __init__.py        # Exposes module-level DFA helper bindings
│   └── dfa.py             # XML parser for JFLAP .jff automaton definitions
│
├── game/
│   ├── pokemon.py         # Pokémon structural data bindings, moves, and HP management
│   └── battle_ui.py       # Pygame screen rendering, event loops, and sequencing logic
│
├── States.jff             # JFLAP Finite State Automaton definition source file
└── main.py                # Engine execution entry point
```

---

## Automaton Specification

The engine evaluates input alphabet symbols ($\Sigma$) mapped directly from combat interactions:

* `d`: Standard damage taken ($\text{HP} > 0$).
* `h`: Standard health restoration (*Synthesis*, *Aqua Ring*, *Potion*).
* `r`: *Rest* recovery input (Charmander).
* `b`: Burn infliction (*Fire Spin*).
* `x`: Poison infliction (*Muddy Water* / *Leech Seed*).
* `p`: Paralysis trigger (*Volt Tackle*).
* `s`: Sleep infliction (*Sleep Powder*, *Sing*).
* `z`: Paralysis stun-check failure trigger.
* `w`: Wake up / un-stun trigger.
* `f`: Faint transition ($\text{HP} \le 0$).

Accepting states ($F = \{q_0, q_1, q_5, q_7\}$) grant `can_attack = True`, whereas single-circle rejecting states block commands and trap afflicted entities until a valid transition symbol clears the condition.

---

## Controls

* **Menu Navigation**: Use the directional **Arrow Keys** (`UP`, `DOWN`, `LEFT`, `RIGHT`) to navigate battle commands or the Pokémon selection roster.
* **Selection / Confirmation**: Press **Enter** (`RETURN`) to select a combatant or lock in an active move.
* **Restart**: Press **Enter** following a victory or defeat screen to return to the roster selection interface.

---

## Getting Started

### Prerequisites

Ensure you have **Python 3.10+** and the **Pygame** library installed within your working environment:

```bash
pip install pygame
```

### Running the Application

Clone or download the repository, navigate to the project root directory, and execute `main.py`:

```bash
python main.py
```

---

## License

This project is distributed under the MIT License. Feel free to use, modify, and expand upon this codebase for educational and portfolio purposes.