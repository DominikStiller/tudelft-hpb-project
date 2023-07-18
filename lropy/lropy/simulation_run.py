import json
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Self, Any

from lropy.util import generate_id, generate_folder_name


class TargetType(Enum):
    Cannonball = 1
    Paneled = 2


class ThermalType(Enum):
    Delayed = 1
    AngleBased = 2
    NoThermal = 3


class AlbedoDistribution(Enum):
    Constant = 1
    DLAM1 = 2
    NoAlbedo = 3


class PanelingType(Enum):
    Static = 1
    Dynamic = 2


class SimulationRun:
    """Models a single simulation run"""

    id: str
    run_number: int
    hostname: str
    start_timestamp: datetime
    base_dir: Path
    save_dir: Path

    simulation_start: str
    simulation_duration: float
    target_type: TargetType
    with_instantaneous_reradiation: bool
    use_occultation: bool
    use_solar_radiation: bool
    use_moon_radiation: bool
    paneling_moon: PanelingType
    albedo_distribution_moon: AlbedoDistribution
    number_of_panels_moon: int
    number_of_panels_per_ring_moon: list[int]
    thermal_type_moon: ThermalType
    step_size: float

    def __init__(self, base_dir: Path, run_number: int = None):
        self.base_dir = base_dir
        self.id = generate_id()
        self.run_number = run_number
        self.hostname = os.getenv("HOSTNAME", "unknown")
        self.start_timestamp = datetime.now()

        if self.run_number is not None:
            self.save_dir = self.base_dir / str(run_number)
        else:
            self.save_dir = self.base_dir / generate_folder_name(self.start_timestamp, self.id)

    @classmethod
    def from_dict(cls, settings: dict[str, Any], base_dir: Path, run_number: int = None) -> Self:
        run = SimulationRun(base_dir, run_number)

        run.simulation_start = settings["simulation_start"]
        run.simulation_duration_revolutions(settings["simulation_duration_rev"])
        run.target_type = settings["target_type"]
        run.with_instantaneous_reradiation = settings["with_instantaneous_reradiation"]
        run.use_occultation = settings["use_occultation"]
        run.use_solar_radiation = settings["use_solar_radiation"]
        run.use_moon_radiation = settings["use_moon_radiation"]
        run.paneling_moon = settings["paneling_moon"]
        run.albedo_distribution_moon = settings["albedo_distribution_moon"]
        run.number_of_panels_moon = settings["number_of_panels_moon"]
        run.number_of_panels_per_ring_moon = settings["number_of_panels_per_ring_moon"]
        run.thermal_type_moon = settings["thermal_type_moon"]
        run.step_size = settings["step_size"]

        return run

    def simulation_duration_revolutions(self, revolutions: float):
        # Averave orbit duration is 113 min
        self.simulation_duration = revolutions * 113 * 60

    def as_json(self) -> str:
        return json.dumps(
            {
                "id": self.id,
                "hostname": self.hostname,
                "start_timestamp": self.start_timestamp.isoformat(),
                "save_dir": str(self.save_dir.resolve()),
                "simulation_start": self.simulation_start,
                "target_type": self.target_type.name,
                "with_instantaneous_reradiation": self.with_instantaneous_reradiation,
                "use_occultation": self.use_occultation,
                "use_solar_radiation": self.use_solar_radiation,
                "use_moon_radiation": self.use_moon_radiation,
                "paneling_moon": (self.paneling_moon.name if self.use_moon_radiation else ""),
                "number_of_panels_moon": (
                    self.number_of_panels_moon
                    if (self.use_moon_radiation and self.paneling_moon == PanelingType.Static)
                    else 0
                ),
                "number_of_panels_per_ring_moon": (
                    self.number_of_panels_per_ring_moon
                    if (self.use_moon_radiation and self.paneling_moon == PanelingType.Dynamic)
                    else []
                ),
                "albedo_distribution_moon": (
                    self.albedo_distribution_moon.name if self.use_moon_radiation else ""
                ),
                "thermal_type_moon": (
                    self.thermal_type_moon.name if self.use_moon_radiation else ""
                ),
                "simulation_duration": self.simulation_duration,
                "step_size": self.step_size,
            },
            indent=3,
        )

    def write_json(self) -> Path:
        self.save_dir.mkdir(parents=True, exist_ok=False)
        path = self.save_dir / "settings.json"
        with open(path, "w") as f:
            f.write(self.as_json())
        return path.resolve()
