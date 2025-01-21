# Goopies

Artificial life project based on physical simulation and neural networks in python.

Agents (blue) called Goopies are placed in an environment where they have to eat food (green) to survive. If they eat enough, they are able to reproduce, with a slight chance of mutations occurring. This combination of mutation and selection creates the conditions for the evolution of traits, which leads to agents more suited to the environment.

Full simulation:
![full simulation](figures/full_simulation.gif)

Close-up of a single evolved Goopie:
![single goopie](figures/single_goopie.gif)

## Installation and running the project

To install all the required dependencies, simply clone the repository and install using pip in your virtual environment.

**N.B.**: Sometimes pyglet can cause problems if installed directly in system packages, so using a virtual environment is **highly** recommended. 

    python -m venv .venv
    source ./venv/bin/activate

Then install all the requirements:

    pip install -r requirements

To run the project simply execute `main.py`:

    python src/main.py