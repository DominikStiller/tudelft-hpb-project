import os
import pickle

from lropy.analysis.io import load_all_simulation_results
from lropy.run.configurator import *
from lropy.run.runner import Runner

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
    # print(len(runs))
    # for run in runs:
    #     print(run.as_json())

    print(f"======== RUNNING {len(runs)} SIMULATIONS ======== ")
    runner.run_all(runs)

    print(f"======== PROCESSING RESULTS ======== ")
    base_dir = runs[0].base_dir
    results = load_all_simulation_results(base_dir, load_runs=True, do_tf=True)
    with (base_dir / "results.pkl").open("wb") as f:
        pickle.dump(results, f)
