import itertools
from pathlib import Path
from typing import Any
from abc import ABC

from lropy.simulation_run import SimulationRun, TargetType, ThermalType, AlbedoDistribution, PanelingType
from lropy.util import generate_folder_name


class Configurator(ABC):
    """Generates runs as combinations of settings"""

    settings: dict[str, list[Any]]
    configuration_name: str

    def _get_settings(self) -> list[dict[str, Any]]:
        # Produce combinations of settings
        # If moon radiation is not used, do not use combinations of moon-specific parameters like number of panels
        all_run_settings = set()
        for single_run_settings in itertools.product(*self.settings.values()):
            single_run_settings = list(single_run_settings)
            target_type = single_run_settings[2]
            use_moon_radiation = single_run_settings[5]
            paneling_moon = single_run_settings[6]

            if not use_moon_radiation:
                single_run_settings[6] = None  # paneling_moon
                single_run_settings[7] = None  # albedo_distribution_moon
                single_run_settings[8] = 0  # number_of_panels_moon
                single_run_settings[9] = []  # number_of_panels_per_ring_moon
                single_run_settings[10] = None  # thermal_type_moon

            if paneling_moon != PanelingType.Static:
                single_run_settings[7] = 0  # number_of_panels_moon

            if paneling_moon != PanelingType.Dynamic:
                single_run_settings[8] = []  # number_of_panels_per_ring_moon

            if target_type != TargetType.Paneled:
                single_run_settings[3] = False  # with_instantaneous_reradiation

            # Necessary to allow hashing for set
            single_run_settings[9] = tuple(single_run_settings[9])

            all_run_settings.add(tuple(single_run_settings))

        return [
            {k: v for k, v in zip(self.settings.keys(), single_run_settings)}
            for single_run_settings in all_run_settings
        ]

    def get_runs(self) -> list[SimulationRun]:
        all_settings = self._get_settings()
        print(f"Generated {len(all_settings)} run settings")

        results_dir = Path("results") / (self.configuration_name + "-" + generate_folder_name())
        runs = [
            SimulationRun.from_dict(settings, results_dir, i + 1)
            for i, settings in enumerate(all_settings)
        ]

        return runs


class FullConfigurator(Configurator):
    def __init__(self):
        self.configuration_name = "full"
        self.settings = {
            "simulation_start": ["2010 JUN 26 06:00:00", "2010 SEP 26 06:00:00"],
            "simulation_duration_rev": [5],  # 565 min, about 5 orbital revolutions
            "target_type": [TargetType.Cannonball, TargetType.Paneled],
            "with_instantaneous_reradiation": [False, True],
            "use_occultation": [False, True],
            "use_moon_radiation": [False, True],
            "paneling_moon": [PanelingType.Dynamic],
            "albedo_distribution_moon": [AlbedoDistribution.Constant, AlbedoDistribution.DLAM1],
            "number_of_panels_moon": [2000],
            "number_of_panels_per_ring_moon": [[6, 12]],
            "thermal_type_moon": [ThermalType.Delayed, ThermalType.AngleBased],
            "step_size": [10],
        }


class NumberOfPanelsConfigurator(Configurator):
    def __init__(self):
        self.configuration_name = "number_of_panels_test"
        self.settings = {
            "simulation_start": ["2010 JUN 26 06:00:00"],
            "simulation_duration_rev": [2],
            "target_type": [TargetType.Cannonball],
            "with_instantaneous_reradiation": [False],
            "use_occultation": [True],
            "use_moon_radiation": [True],
            "paneling_moon": [PanelingType.Static],
            "albedo_distribution_moon": [AlbedoDistribution.DLAM1],
            "number_of_panels_moon": [2000, 5000, 10000, 20000, 50000],
            "number_of_panels_per_ring_moon": [[]],
            "thermal_type_moon": [ThermalType.AngleBased],
            "step_size": [10],
        }


class NumberOfPanelsPerRingConfigurator(Configurator):
    def __init__(self):
        self.configuration_name = "number_of_panels_per_ring_test"
        self.settings = {
            "simulation_start": ["2010 JUN 26 06:00:00"],
            "simulation_duration_rev": [2],
            "target_type": [TargetType.Cannonball],
            "with_instantaneous_reradiation": [False],
            "use_occultation": [True],
            "use_moon_radiation": [True],
            "paneling_moon": [PanelingType.Dynamic],
            "albedo_distribution_moon": [AlbedoDistribution.DLAM1],
            "number_of_panels_moon": [2000],
            "number_of_panels_per_ring_moon": [[6, 12], [12, 24], [12, 24, 36], [24, 36, 48]],
            "thermal_type_moon": [ThermalType.AngleBased],
            "step_size": [10],
        }


class StaticVsDynamicConfigurator(Configurator):
    def __init__(self):
        self.configuration_name = "static_vs_dynamic"
        self.settings = {
            "simulation_start": ["2010 JUN 26 06:00:00"],
            "simulation_duration_rev": [2],
            "target_type": [TargetType.Cannonball],
            "with_instantaneous_reradiation": [False],
            "use_occultation": [True],
            "use_moon_radiation": [True],
            "paneling_moon": [PanelingType.Static, PanelingType.Dynamic],
            "albedo_distribution_moon": [AlbedoDistribution.Constant, AlbedoDistribution.DLAM1],
            "number_of_panels_moon": [5000],
            "number_of_panels_per_ring_moon": [[24, 36, 48]],
            "thermal_type_moon": [ThermalType.AngleBased],
            "step_size": [10],
        }
