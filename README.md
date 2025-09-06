# Pokemon-MCP-Tool

This project implements an MCP (Model Context Protocol) server providing AI models access to Pokémon data and a battle simulation tool. It allows Large Language Models (LLMs) to query comprehensive Pokémon information and simulate turn-based battles with core mechanics like type effectiveness and status effects. The server is designed to be integrated easily with the Claude desktop app.

---

## Features

### Pokémon Data Resource
- Access detailed Pokémon data including:
  - Base stats (HP, Attack, Defense, Special Attack, Special Defense, Speed)
  - Types (Fire, Water, Grass, etc.)
  - Abilities with effects
  - Available moves (with descriptions)
  - Evolution chains
- Provides an MCP resource interface to expose this data to LLMs.

### Battle Simulation Tool
- Simulate battles between any two Pokémon by name.
- Implements core Pokémon battle mechanics including:
  - Type effectiveness calculations
  - Damage calculations using stats and move power
  - Turn order based on Speed stats
  - Status effects: Paralysis, Burn, Poison
- Provides detailed battle logs describing each action and outcome.
- Determines a winner based on which Pokémon faints first.
- Exposed as an MCP tool interface for use by LLMs.

---

## Project Structure

- `server.py` - Main MCP server with Pokemon data and battle simulation tools.
- `pokemon_data.py` - Fetches and processes Pokemon data from the public PokeAPI.
- `battle_calculations.py` - Contains mechanics for damage, status effects, and type effectiveness.
- `static_data.py` - Static constants like type effectiveness multipliers and status effects.
- `test.py` - Sample test script demonstrating the usage of Pokemon data functions and battle calculations.
- `requirements.txt` - Python dependencies needed to run the server.

---

## Setup and Installation

### Prerequisites
- Python 3.8+
- Internet access to query the public PokeAPI
- MCP framework (`mcp` package)
- `httpx` for async HTTP requests

### Steps to run :
1. Clone this repository:
```bash
git clone https://github.com/AryanAhmadChaudhary/Pokemon-MCP-Tool.git
```

2. Change to the project root directory:
```bash
cd Pokemon-MCP-Tool
```

3. Install dependencies:
```bsh
pip install -r requirements.txt
```
4. Run the MCP server (this will start the MCP inspector UI):
```bash
uv run mcp dev server.py
```
Confirm the MCP inspector opens successfully and you can interact with your tools.

5. Verify MCP configuration and run the dev server to connect with claude:
```bash 
uv run mcp dev server.py
```
6. Once installed, you can run and interact with the Pokémon data and battle simulation tools directly inside Claude's interface.

---

## Usage Examples

### Query Pokémon Info
Ask the MCP server for detailed information about a Pokémon by name, including stats, types, abilities, and evolution.

### Simulate Battle
Request a battle simulation between two Pokémon. The server will return a detailed battle log and the winner.

---