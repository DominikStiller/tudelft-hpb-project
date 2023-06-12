import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

from lropy.simulation_run import (
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
            futures = []
            for run in runs:
                futures.append(executor.submit(self.run_single, run))
            for future in as_completed(futures):
                future.result()

    def run_single(self, run: SimulationRun):
        tudat_dir = Path.home() / "dev/tudat-bundle"
        executable = tudat_dir / "build/tudat/bin/application_lro_json"
        json_path = run.write_json()

        output_file = open(run.save_dir / "out.txt", "w")

        with self.lock:
            self.n_started += 1
            print(f"[{self.n_started}/{self.n_total}] Run {run.id} started")

        p = subprocess.Popen(
            [executable, str(json_path)], cwd=tudat_dir, stdout=output_file, stderr=output_file
        )
        return_code = p.wait()

        output_file.close()

        with self.lock:
            self.n_finished += 1
            print(
                f"[{self.n_finished}/{self.n_total}] Run {run.id} finished (code {return_code}), "
                f"results stored in {run.save_dir}"
            )


if __name__ == "__main__":
    run = SimulationRun(Path("results"))

    run.simulation_start = "2010 JUN 26 06:00:00"
    run.simulation_duration = 100
    # run.simulation_duration_revolutions(5)
    run.target_type = TargetType.Paneled
    run.with_instantaneous_reradiation = False
    run.use_occultation = True
    run.use_solar_radiation = True
    run.use_moon_radiation = True
    run.paneling_moon = PanelingType.Dynamic
    run.albedo_distribution_moon = AlbedoDistribution.DLAM1
    run.number_of_panels_moon = 2000
    run.number_of_panels_per_ring_moon = [6, 15]
    run.thermal_type_moon = ThermalType.Delayed
    run.step_size = 10

    # print(run.write_json())
    Runner().run_single(run)
