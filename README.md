# 🧬 LifePong

A creative fusion of Pong and Conway's Game of Life, implemented using Pygame.  

---

## 🎮 Overview

LifePong reimagines the classic Pong game by integrating the principles of Conway's Game of Life.  
Players place living cells on their side of the board, which evolve over time and act as paddles to interact with the ball.  
This dynamic creates a unique and unpredictable gameplay experience.

---

## 📋 Features

- **Cell Placement**: Players can place or remove cells on their side of the board using the mouse or by dragging for quick input.  
- **Cell Evolution**: Cells evolve each frame based on the Game of Life rules, affecting the movement and interaction with the ball.  
- **AI Integration**: Future plans include implementing AI to place paddles, making the game more challenging.  
- **Pygame Implementation**: Built using Pygame, providing smooth graphics and real-time interaction.  

---

## 🧪 Rules

At the beginning of each round, players have 40 cells to place/remove (make alive/kill) on their side of the board using the mouse (you can also drag for quick input). These and their future generations will work as paddles of the original Pong game.  

At each step in time, the following transitions occur:

- Any live cell with fewer than two live neighbours dies, as if by underpopulation.  
- Any live cell with two or three live neighbours lives on to the next generation.  
- Any live cell with more than three live neighbours dies, as if by overpopulation.  
- Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.  

These rules create a dynamic environment where the paddles' behavior is influenced by the evolving cell patterns.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x  
- Pygame library

### Installation

1. Clone the repository:

```bash
git clone https://github.com/MahanNoosh/LifePong.git
```
2. Install dependencies:
```bash
pip install pygame
```
3. Run the game:
```bash
python main.py
```

--- 

## 🤖 Future Enhancements

- AI Players: Develop AI algorithms to place paddles, enhancing gameplay complexity.
- Multiplayer Mode: Implement online multiplayer functionality.
- Advanced Visuals: Improve graphics and animations for a more immersive experience.
- Sound Effects: Add sound effects to enhance user engagement.
