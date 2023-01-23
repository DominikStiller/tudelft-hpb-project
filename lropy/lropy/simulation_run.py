import json
from datetime import datetime
from enum import Enum
from pathlib import Path

from lropy.util import generate_id, generate_folder_name


class TargetType(Enum):
    Cannonball = 1
    Paneled = 2


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
    use_moon_radiation: bool
    number_of_panels_moon: int
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
                "use_moon_radiation": self.use_moon_radiation,
                "number_of_panels_moon": (
                    self.number_of_panels_moon if self.use_moon_radiation else 0
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
