from simulation import Simulation

# parse arguments
HEADLESS = False


if __name__ == "__main__":

    if HEADLESS:
        # Before arcade is imported
        import os
        os.environ["ARCADE_HEADLESS"] = "True"

    sim = Simulation(20, 0, 500)
    sim.run(HEADLESS)