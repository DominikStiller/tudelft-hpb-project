import itertools
from pathlib import Path
from typing import Any

from lropy.simulation_run import SimulationRun, TargetType, ThermalType
from lropy.util import generate_folder_name


class Configurator:
    """Generates runs as combinations of settings"""

    def __init__(self):
        self.settings = {
            "simulation_start": ["2010 JUN 26 06:00:00", "2010 SEP 26 06:00:00"],
            "simulation_duration_rev": [5],  # 565 min, about 5 orbital revolutions
            "target_type": [TargetType.Cannonball, TargetType.Paneled],
            "use_occultation": [False, True],
            "use_moon_radiation": [False, True],
            "number_of_panels_moon": [2000, 5000, 20000],
            "thermal_type": [ThermalType.Delayed, ThermalType.AngleBased],
            "use_instantaneous_reradiation": [False, True],
            "step_size": [10],
        }

    def _get_settings(self) -> list[dict[str, Any]]:
        # Produce combinations of settings
        # If moon radiation is not used, do not use combinations of moon-specific parameters like number of panels
        all_run_settings = set()
        for single_run_settings in itertools.product(*self.settings.values()):
            single_run_settings = list(single_run_settings)
            use_moon_radiation = single_run_settings[4]
            if not use_moon_radiation:
                single_run_settings[5] = 0  # number_of_panels_moon
                single_run_settings[6] = None  # thermal_type
                single_run_settings[7] = False  # use_instantaneous_reradiation
            all_run_settings.add(tuple(single_run_settings))

        return [
            {k: v for k, v in zip(self.settings.keys(), single_run_settings)}
            for single_run_settings in all_run_settings
        ]

    def get_runs(self) -> list[SimulationRun]:
        all_settings = self._get_settings()
        print(f"Generated {len(all_settings)} run settings")

        run_set_dir = Path("results") / generate_folder_name()
        runs = [
            SimulationRun.from_dict(settings, run_set_dir, i + 1)
            for i, settings in enumerate(all_settings)
        ]

        return runs
