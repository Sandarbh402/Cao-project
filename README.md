# Cache Memory Performance Simulator

A comprehensive simulation tool for analyzing cache memory performance, featuring both Command Line Interface (CLI) and Graphical User Interface (GUI) versions. This project allows users to configure cache parameters and visualize memory access behavior.

## Features

- **Multiple Mapping Types**:
  - Direct Mapping
  - Fully Associative Mapping
  - Set Associative Mapping (Configurable ways)
- **Replacement Policies**:
  - LRU (Least Recently Used)
  - FIFO (First-In-First-Out)
  - Random Replacement
- **Analytics & Metrics**:
  - Hit/Miss Ratio calculation
  - AMAT (Average Memory Access Time) analysis
  - Detailed access trace with tags, indices, and offsets
- **Visualization & Export**:
  - CSV export of simulation traces
  - Comparison charts for different configurations (PNG)
  - GUI built with Tkinter for interactive simulation

## Project Structure

```text
├── modules/
│   ├── module1_config.py    # Cache configuration logic
│   ├── module2_cache.py     # Main cache simulation engine
│   ├── module3_replacement.py # Replacement policy implementations
│   ├── module4_trace.py     # Memory access trace management
│   └── module5_analytics.py   # Result processing and visualization
├── run_cli.py               # CLI entry point
├── run_gui.py               # GUI entry point
└── .gitignore               # Version control exclusion
```

## How to Run

### Command Line Interface (CLI)
To run the CLI version, use:
```bash
python run_cli.py
```

### Graphical User Interface (GUI)
To run the GUI version, use:
```bash
python run_gui.py
```

## Requirements
- Python 3.x
- `matplotlib` (Optional, required for comparison charts)
- `tkinter` (Usually included with Python)

## Team
- Romit Raman
- Sandarbh Gupta
- Shivansh Verma
