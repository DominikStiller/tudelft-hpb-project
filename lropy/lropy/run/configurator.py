import itertools
from pathlib import Path
from typing import Any

from lropy.run.simulation_run import (
    SimulationRun,
    TargetType,
    ThermalType,
    AlbedoDistribution,
    PanelingType,
)
from lropy.run.util import generate_folder_name


class Configurator:
    """Generates runs as combinations of settings"""

    def __init__(
        self,
        configuration_name: str,
        settings: dict[str, list[Any]],
        is_benchmark: bool,
        add_baseline: bool = True,
    ):
        self.configuration_name = configuration_name
        self.settings = settings
        self.is_benchmark = is_benchmark
        self.add_baseline = add_baseline

        if self.is_benchmark:
            self.configuration_name += "-benchmark"

    def _get_settings(self) -> list[dict[str, Any]]:
        # Produce combinations of settings
        # If moon radiation is not used, do not use combinations of moon-specific parameters like number of panels
        all_run_settings = set()
        for single_run_settings in itertools.product(*self.settings.values()):
            single_run_settings = list(single_run_settings)
            target_type = single_run_settings[2]
            use_sun_radiation = single_run_settings[5]
            use_moon_radiation = single_run_settings[6]
            paneling_moon = single_run_settings[7]
            albedo_distribution_moon = single_run_settings[8]
            thermal_type_moon = single_run_settings[11]

            if (
                albedo_distribution_moon == AlbedoDistribution.NoAlbedo
                and thermal_type_moon == ThermalType.NoThermal
            ) or (not use_sun_radiation and not use_moon_radiation):
                continue

            if not use_moon_radiation:
                single_run_settings[7] = None  # paneling_moon
                single_run_settings[8] = None  # albedo_distribution_moon
                single_run_settings[9] = 0  # number_of_panels_moon
                single_run_settings[10] = []  # number_of_panels_per_ring_moon
                single_run_settings[11] = None  # thermal_type_moon

            if paneling_moon != PanelingType.Static:
                single_run_settings[9] = 0  # number_of_panels_moon

            if paneling_moon != PanelingType.Dynamic:
                single_run_settings[10] = []  # number_of_panels_per_ring_moon

            if target_type != TargetType.Paneled:
                single_run_settings[3] = False  # with_instantaneous_reradiation

            # Necessary to allow hashing for set
            single_run_settings[10] = tuple(single_run_settings[10])

            all_run_settings.add(tuple(single_run_settings))

        settings = [
            {k: v for k, v in zip(self.settings.keys(), single_run_settings)}
            for single_run_settings in all_run_settings
        ]
        for setting in settings:
            setting["save_results"] = not self.is_benchmark
        return settings

    def _get_baseline_settings(self, base_settings: dict):
        baseline_settings = []
        for simulation_start in self.settings["simulation_start"]:
            settings = base_settings.copy()
            settings.update(
                {
                    "simulation_start": simulation_start,
                    "use_solar_radiation": False,
                    "use_moon_radiation": False,
                }
            )
            baseline_settings.append(settings)
        return baseline_settings

    def get_runs(self) -> list[SimulationRun]:
        all_settings = self._get_settings()
        if self.add_baseline:
            all_settings.extend(self._get_baseline_settings(all_settings[0]))
        print(f"Generated {len(all_settings)} run settings")

        results_dir = Path("../results") / (self.configuration_name + "-" + generate_folder_name())
        runs = [
            SimulationRun.from_dict(settings, results_dir, i + 1)
            for i, settings in enumerate(all_settings)
        ]

        return runs


class SingleConfigurator(Configurator):
    def __init__(self, is_benchmark: bool = False):
        super().__init__(
            "single",
            {
                "simulation_start": ["2011 SEP 26 18:00:00"],
                "simulation_duration_rev": [32],  # 2.5 days, about 32 orbital revolutions
                "target_type": [TargetType.Paneled],
                "with_instantaneous_reradiation": [True],
                "use_occultation": [True],
                "use_solar_radiation": [True],
                "use_moon_radiation": [True],
                "paneling_moon": [PanelingType.Dynamic],
                "albedo_distribution_moon": [AlbedoDistribution.DLAM1],
                "number_of_panels_moon": [5000],
                "number_of_panels_per_ring_moon": [[6, 12, 18, 24, 30]],
                "thermal_type_moon": [ThermalType.AngleBased],
                "step_size": [5],
            },
            is_benchmark,
            add_baseline=False,
        )


class FullConfigurator(Configurator):
    # Used for paper
    def __init__(self, is_benchmark: bool = False):
        super().__init__(
            "full",
            {
                "simulation_start": ["2010 JUN 28 15:00:00", "2011 SEP 26 18:00:00"],
                "simulation_duration_rev": [32],  # 2.5 days, about 32 orbital revolutions
                "target_type": [TargetType.Cannonball, TargetType.Paneled],
                "with_instantaneous_reradiation": [True],
                "use_occultation": [True],
                "use_solar_radiation": [False, True],
                "use_moon_radiation": [False, True],
                "paneling_moon": [PanelingType.Dynamic],
                "albedo_distribution_moon": [
                    AlbedoDistribution.NoAlbedo,
                    AlbedoDistribution.Constant,
                    AlbedoDistribution.DLAM1,
                ],
                "number_of_panels_moon": [5000],
                "number_of_panels_per_ring_moon": [[6, 12, 18, 24, 30, 36]],
                "thermal_type_moon": [
                    ThermalType.NoThermal,
                    ThermalType.AngleBased,
                ],
                "step_size": [5],
            },
            is_benchmark,
        )


class FullBenchmarkConfigurator(Configurator):
    # Used for paper
    def __init__(self, is_benchmark: bool = True):
        super().__init__(
            "full",
            {
                "simulation_start": ["2010 JUN 28 15:00:00"],
                "simulation_duration_rev": [32],  # 2.5 days, about 32 orbital revolutions
                "target_type": [TargetType.Cannonball, TargetType.Paneled],
                "with_instantaneous_reradiation": [True],
                "use_occultation": [True],
                "use_solar_radiation": [False, True],
                "use_moon_radiation": [False, True],
                "paneling_moon": [PanelingType.Dynamic],
                "albedo_distribution_moon": [
                    AlbedoDistribution.Constant,
                    AlbedoDistribution.DLAM1,
                ],
                "number_of_panels_moon": [5000],
                "number_of_panels_per_ring_moon": [[6, 12, 18, 24, 30, 36]],
                "thermal_type_moon": [
                    ThermalType.AngleBased,
                ],
                "step_size": [5],
            },
            is_benchmark,
        )


class LightConfigurator(Configurator):
    # Used for poster
    def __init__(self, is_benchmark: bool = False):
        super().__init__(
            "light",
            {
                "simulation_start": ["2010 SEP 26 06:00:00"],
                "simulation_duration_rev": [32],  # 2.5 days, about 32 orbital revolutions
                "target_type": [TargetType.Cannonball, TargetType.Paneled],
                "with_instantaneous_reradiation": [False],
                "use_occultation": [True],
                "use_solar_radiation": [True],
                "use_moon_radiation": [False, True],
                "paneling_moon": [PanelingType.Static],
                "albedo_distribution_moon": [
                    AlbedoDistribution.Constant,
                    AlbedoDistribution.DLAM1,
                ],
                "number_of_panels_moon": [70000],
                "number_of_panels_per_ring_moon": [[]],
                "thermal_type_moon": [ThermalType.AngleBased],
                "step_size": [10],
            },
            is_benchmark,
        )


class NumberOfStaticPanelsConfigurator(Configurator):
    def __init__(self, is_benchmark: bool = False):
        super().__init__(
            "number_of_panels_test",
            {
                "simulation_start": ["2010 JUN 26 06:00:00"],
                "simulation_duration_rev": [2],
                "target_type": [TargetType.Cannonball],
                "with_instantaneous_reradiation": [False],
                "use_occultation": [True],
                "use_solar_radiation": [True],
                "use_moon_radiation": [True],
                "paneling_moon": [PanelingType.Static],
                "albedo_distribution_moon": [AlbedoDistribution.DLAM1],
                "number_of_panels_moon": [2000, 5000, 10000, 20000, 50000],
                "number_of_panels_per_ring_moon": [[]],
                "thermal_type_moon": [ThermalType.AngleBased],
                "step_size": [10],
            },
            is_benchmark,
        )


class NumberOfPanelsPerRingConfigurator(Configurator):
    def __init__(self, is_benchmark: bool = False):
        super().__init__(
            "number_of_panels_per_ring_test",
            {
                "simulation_start": ["2010 AUG 26 06:00:00"],
                "simulation_duration_rev": [2],
                "target_type": [TargetType.Cannonball],
                "with_instantaneous_reradiation": [False],
                "use_occultation": [True],
                "use_solar_radiation": [True],
                "use_moon_radiation": [True],
                "paneling_moon": [PanelingType.Dynamic],
                "albedo_distribution_moon": [
                    AlbedoDistribution.Constant,
                    AlbedoDistribution.DLAM1,
                ],
                "number_of_panels_moon": [2000],
                "number_of_panels_per_ring_moon": [
                    [6],
                    [6, 12],
                    [6, 12, 18],
                    [6, 12, 18, 24],
                    [6, 12, 18, 24, 30],
                    [6, 12, 18, 24, 30, 36],
                    [6, 12, 18, 24, 30, 36, 42],
                    [6, 12, 18, 24, 30, 36, 42, 48],
                    [6, 12, 18, 24, 30, 36, 42, 48, 56],
                    [6, 12, 18, 24, 30, 36, 42, 48, 56, 60],
                    [6, 12, 18, 24, 30, 36, 42, 48, 56, 60, 66],
                    [6, 12, 18, 24, 30, 36, 42, 48, 56, 60, 66, 72],
                    [6, 12, 18, 24, 30, 36, 42, 48, 56, 60, 66, 72, 78],
                    [6, 12, 18, 24, 30, 36, 42, 48, 56, 60, 66, 72, 78, 84],
                    [6, 12, 18, 24, 30, 36, 42, 48, 56, 60, 66, 72, 78, 84, 90],
                ],
                "thermal_type_moon": [ThermalType.AngleBased],
                "step_size": [10],
            },
            is_benchmark,
        )


class InstantaneousReradiationConfigurator(Configurator):
    def __init__(self, is_benchmark: bool = False):
        super().__init__(
            "instantaneous_reradiation_test",
            {
                "simulation_start": ["2010 JUN 28 15:00:00", "2011 SEP 26 18:00:00"],
                "simulation_duration_rev": [2],
                "target_type": [TargetType.Paneled],
                "with_instantaneous_reradiation": [False, True],
                "use_occultation": [True],
                "use_solar_radiation": [True],
                "use_moon_radiation": [True],
                "paneling_moon": [PanelingType.Dynamic],
                "albedo_distribution_moon": [AlbedoDistribution.Constant],
                "number_of_panels_moon": [2000],
                "number_of_panels_per_ring_moon": [[6, 12, 18, 24, 30, 36]],
                "thermal_type_moon": [ThermalType.AngleBased],
                "step_size": [5],
            },
            is_benchmark,
        )


class AlbedoThermalConfigurator(Configurator):
    def __init__(self, is_benchmark: bool = False):
        super().__init__(
            "albedo_thermal_test",
            {
                "simulation_start": [
                    "2010 JUN 28 15:00:00",
                    "2010 AUG 4 15:00:00",
                    "2011 SEP 26 18:00:00",
                ],
                "simulation_duration_rev": [2],
                "target_type": [TargetType.Cannonball, TargetType.Paneled],
                "with_instantaneous_reradiation": [True],
                "use_occultation": [True],
                "use_solar_radiation": [True],
                "use_moon_radiation": [True],
                "paneling_moon": [PanelingType.Dynamic],
                "albedo_distribution_moon": [
                    AlbedoDistribution.NoAlbedo,
                    AlbedoDistribution.Constant,
                    AlbedoDistribution.DLAM1,
                ],
                "number_of_panels_moon": [2000],
                "number_of_panels_per_ring_moon": [[6, 12, 18, 24, 30, 36]],
                "thermal_type_moon": [
                    ThermalType.NoThermal,
                    ThermalType.AngleBased,
                    ThermalType.Delayed,
                ],
                "step_size": [5],
            },
            is_benchmark,
        )


class StaticVsDynamicConfigurator(Configurator):
    def __init__(self, is_benchmark: bool = False):
        super().__init__(
            "static_vs_dynamic",
            {
                "simulation_start": ["2010 JUN 26 06:00:00", "2010 SEP 26 06:00:00"],
                "simulation_duration_rev": [2],
                "target_type": [TargetType.Cannonball],
                "with_instantaneous_reradiation": [False],
                "use_occultation": [False],
                "use_solar_radiation": [True],
                "use_moon_radiation": [True],
                "paneling_moon": [PanelingType.Static, PanelingType.Dynamic],
                "albedo_distribution_moon": [
                    AlbedoDistribution.Constant,
                    AlbedoDistribution.DLAM1,
                ],
                "number_of_panels_moon": [70000],
                "number_of_panels_per_ring_moon": [
                    [6, 12],
                    [6, 12, 18, 24, 30, 36, 42, 48, 56, 60],
                ],
                "thermal_type_moon": [ThermalType.NoThermal],
                "step_size": [10],
            },
            is_benchmark,
        )
