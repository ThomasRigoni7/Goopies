from simulation import Simulation

# parse arguments
HEADLESS = False
TEST = False

if __name__ == "__main__":

    if HEADLESS:
        # Before arcade is imported
        import os
        os.environ["ARCADE_HEADLESS"] = "True"

    if TEST:
        sim = Simulation(1, 1, 200, TEST)
    else:
        sim = Simulation(20, 500, 5000, blueprint="checkpoints/manual/net.pt")
        # sim = Simulation(100, 2000, 2500)
    sim.run(HEADLESS)