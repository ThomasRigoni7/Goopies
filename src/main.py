from simulation import Simulation

# parse arguments
HEADLESS = False


if __name__ == "__main__":

    if HEADLESS:
        # Before arcade is imported
        import os
        os.environ["ARCADE_HEADLESS"] = "True"

    sim = Simulation(100, 0, 2500)
    sim.run(HEADLESS)