import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, wait
from pathlib import Path
from threading import Lock

from lropy.analysis.spice_tools import spice_base
from lropy.run.simulation_run import (
    SimulationRun,
    TargetType,
    ThermalType,
    AlbedoDistribution,
    PanelingType,
)


class Runner:
    """Executes a single or multiple runs in parallel"""

    n_total: int
    n_started: int
    n_finished: int
    lock: Lock = Lock()

    n_threads: int

    def __init__(self, n_threads: int = None):
        self.n_threads = n_threads
        self._reset()

    def _reset(self):
        with self.lock:
            self.n_started = 0
            self.n_finished = 0
            self.n_total = 1

    def run_all(self, runs: list[SimulationRun]):
        self._reset()
        self.n_total = len(runs)

        with ThreadPoolExecutor(max_workers=self.n_threads) as executor:
            fut = [executor.submit(self.run_single, run) for run in runs]
            wait(fut)
            for f in fut:
                f.result()

    def run_single(self, run: SimulationRun):
        project_folder = Path("..")
        executable = project_folder / "simulations/build/bin/application_lro_json"
        json_path = run.write_json()

        with self.lock:
            self.n_started += 1
            print(f"[{self.n_started}/{self.n_total}] Run {run.id} started")

        time_start = time.perf_counter()

        if run.save_results:
            output_file = run.save_dir / "out.txt"
        else:
            output_file = os.devnull

        output_file = open(output_file, "w")
        p = subprocess.Popen(
            [executable, str(json_path)],
            stdout=output_file,
            stderr=output_file,
            env={**os.environ, "SPICE_BASE": f"{spice_base}/"},
        )
        return_code = p.wait()
        time_end = time.perf_counter()
        output_file.close()

        with open(run.save_dir / "walltime.txt", "a") as f:
            f.write(f"{time_end - time_start}\n")

        with self.lock:
            self.n_finished += 1
            print(
                f"[{self.n_finished}/{self.n_total}] Run {run.id} finished (code {return_code}), "
                f"results stored in {run.save_dir}"
            )


if __name__ == "__main__":
    run = SimulationRun(Path("../results"))

    run.simulation_start = "2010 SEP 26 16:30:00"
    # run.simulation_duration = 100
    run.simulation_duration_revolutions(1)
    run.target_type = TargetType.Paneled
    run.with_instantaneous_reradiation = True
    run.use_occultation = True
    run.use_solar_radiation = True
    run.use_moon_radiation = True
    run.paneling_moon = PanelingType.Dynamic
    run.albedo_distribution_moon = AlbedoDistribution.DLAM1
    run.number_of_panels_moon = 70000
    run.number_of_panels_per_ring_moon = [6, 12, 18, 24, 30]
    run.thermal_type_moon = ThermalType.AngleBased
    run.step_size = 10
    run.save_results = True

    # print(run.write_json())
    Runner().run_single(run)
