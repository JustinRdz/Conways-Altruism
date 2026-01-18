# CWOL — Cellular World of Life

CWOL is an experimental cellular automaton designed to explore
evolutionary dynamics and the emergence of altruistic behaviors.

The project serves as a sandbox for comparing:
- Generational evolutionary systems (e.g. CWOL / Game of Life variants)
- Continuous-time systems (e.g. Particle Life)

## Project Structure

- `src/` — main CWOL implementation
- `experiments/` — alternative models and prototypes
- `experiments/particle_life.py` — continuous dynamics experiment
- `experiments/cwol_cpp/` — C++ performance prototype

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt