import os

from lropy.configurator import Configurator
from lropy.runner import Runner

if __name__ == "__main__":
    if os.getenv("HOSTNAME") == "eudoxos":
        n_threads = 12
    else:
        n_threads = 4

    runner = Runner(n_threads)
    configurator = Configurator()
    runs = configurator.get_runs()
    runner.run_all(runs)
