import os
import sys

from lropy.configurator import (
    FullConfigurator,
    LightConfigurator,
    NumberOfPanelsPerRingConfigurator,
    StaticVsDynamicConfigurator,
    InstantaneousReradiationConfigurator,
    AlbedoThermalConfigurator,
)
from lropy.runner import Runner
from lropy.util import get_average_load

if __name__ == "__main__":
    if os.getenv("HOSTNAME") == "eudoxos":
        n_threads = 24
    else:
        n_threads = 4

    # if get_average_load() > 0.2:
    #     # Prevent interference with other users
    #     print(f"Current average load of {get_average_load()} too high")
    #     sys.exit(-1)

    runner = Runner(n_threads)

    # configurator = FullConfigurator()
    # configurator = NumberOfPanelsPerRingConfigurator()
    # configurator = InstantaneousReradiationConfigurator()
    configurator = AlbedoThermalConfigurator()
    # configurator = StaticVsDynamicConfigurator()

    runs = configurator.get_runs()
    # for run in runs:
    #     print(run.as_json())
    runner.run_all(runs)
