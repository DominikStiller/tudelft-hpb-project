import os
import sys

from lropy.configurator import FullConfigurator, NumberOfPanelsConfigurator, NumberOfPanelsPerRingConfigurator, StaticVsDynamicConfigurator
from lropy.runner import Runner
from lropy.util import get_average_load

if __name__ == "__main__":
    if os.getenv("HOSTNAME") == "eudoxos":
        n_threads = 8
    else:
        n_threads = 4

    # if get_average_load() > 0.2:
    #     # Prevent interference with other users
    #     print(f"Current average load of {get_average_load()} too high")
    #     sys.exit(-1)

    runner = Runner(n_threads)
    configurator = FullConfigurator()
    # configurator = NumberOfPanelsConfigurator()
    # configurator = NumberOfPanelsPerRingConfigurator()
    # configurator = StaticVsDynamicConfigurator()
    runs = configurator.get_runs()
    runner.run_all(runs)
