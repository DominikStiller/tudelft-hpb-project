import json
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


class SimulationRun:
    """Models a single simulation run"""

    id: str
    run_number: int
    start_timestamp: datetime
    base_dir: Path
    save_dir: Path

    simulation_start: str
    simulation_duration: float
    target_type: TargetType
    use_occultation: bool
    use_moon_radiation: bool
    number_of_panels_moon: int
    thermal_type: ThermalType
    use_instantaneous_reradiation: bool
    step_size: float

    def __init__(self, base_dir: Path, run_number: int = None):
        self.base_dir = base_dir
        self.id = generate_id()
        self.run_number = run_number
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
        run.use_occultation = settings["use_occultation"]
        run.use_moon_radiation = settings["use_moon_radiation"]
        run.number_of_panels_moon = settings["number_of_panels_moon"]
        run.thermal_type = settings["thermal_type"]
        run.use_instantaneous_reradiation = settings["use_instantaneous_reradiation"]
        run.step_size = settings["step_size"]

        return run

    def simulation_duration_revolutions(self, revolutions: float):
        # Averave orbit duration is 113 min
        self.simulation_duration = revolutions * 113 * 60

    def as_json(self) -> str:
        return json.dumps(
            {
                "id": self.id,
                "start_timestamp": self.start_timestamp.isoformat(),
                "save_dir": str(self.save_dir.resolve()),
                "simulation_start": self.simulation_start,
                "target_type": self.target_type.name,
                "use_occultation": self.use_occultation,
                "use_moon_radiation": self.use_moon_radiation,
                "number_of_panels_moon": (
                    self.number_of_panels_moon if self.use_moon_radiation else 0
                ),
                "thermal_type": (self.thermal_type.name if self.use_moon_radiation else ""),
                "use_instantaneous_reradiation": (
                    self.use_instantaneous_reradiation if self.use_moon_radiation else False
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
