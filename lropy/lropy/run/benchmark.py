import os
import random

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

import pickle

from lropy.analysis.io import load_all_simulation_results
from lropy.run.runner import Runner
from lropy.run.configurator import *

if __name__ == "__main__":
    if os.getenv("HOSTNAME") == "eudoxos":
        n_threads = 27
    else:
        n_threads = 4

    n_iterations = 100

    runner = Runner(n_threads)

    configurator = FullBenchmarkConfigurator(True)

    runs = configurator.get_runs()
    runs = runs * n_iterations
    random.shuffle(runs)

    print(f"======== RUNNING {len(runs)} SIMULATIONS ======== ")
    runner.run_all(runs)

    print(f"======== PROCESSING RESULTS ======== ")
    base_dir = runs[0].base_dir
    results = load_all_simulation_results(base_dir, load_runs=False, n_workers=n_threads)
    with (base_dir / "results.pkl").open("wb") as f:
        pickle.dump(results, f)
