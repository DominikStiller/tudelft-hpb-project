import csv
import json
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Union, Tuple

import numpy as np
import pandas as pd
# noinspection PyUnresolvedReferences
import swifter
from tqdm import tqdm

from lropy.analysis.spice_tools import as_utc
from lropy.analysis.transform import cart2track

swifter.set_defaults(progress_bar=False)


pos_names = ["pos_x", "pos_y", "pos_z"]
vel_names = ["vel_x", "vel_y", "vel_z"]
acc_names = [
    "acc_grav_moon",
    "acc_grav_earth",
    "acc_grav_sun",
    "acc_rp_sun",
    "acc_rp_moon",
    "acc_rp_earth",
    "acc_rp_mercury",
]
irr_names = ["irr_sun", "irr_moon"]
panels_count_names = ["panels_vis_moon", "panels_ill_moon", "panels_vis_ill_moon"]


def _get_column_names(result_dir: Path):
    colnames = []

    with (result_dir / "dependent_variable_names.csv").open(newline="") as f:
        for var in csv.DictReader(f, delimiter=";"):
            name = _get_column_name(var["ID"])
            size = int(var["Size"])
            if size == 1:
                # Scalar
                colnames.append(name)
            else:
                if size == 3:
                    # Vector
                    elements = ["x", "y", "z"]
                elif size == 9:
                    # Row-major matrix
                    elements = ["r11", "r12", "r13", "r21", "r22", "r23", "r31", "r32", "r33"]
                elif name == "kepler":
                    elements = ["a", "e", "i", "argPeri", "longAscNode", "trueAnom"]
                else:
                    raise Exception(f"Unrecognized variable {name}")

                colnames.extend([f"{name}_{elem}" for elem in elements])

    return colnames


def _get_column_name(id: str) -> str:
    if match := re.fullmatch(r"Relative (position|velocity) of (\S+) w.r.t. (\S+)", id):
        type, target, observer = match.groups()

        prefix = type[:3]

        if target in ["LRO", "MPO", "Vehicle"]:
            return prefix
        else:
            return f"{prefix}_{target.lower()}"
    elif match := re.fullmatch(r"Kepler elements of (\S+) w.r.t. (\S+)", id):
        return "kepler"
    elif match := re.fullmatch(r"Altitude of (\S+) w.r.t. (\S+)", id):
        return "h"
    elif match := re.fullmatch(r"TNW to inertial frame rotation matrix of (\S+) w.r.t. (\S+)", id):
        target, central = match.groups()
        return f"rot_{target}_{central}"
    elif match := re.fullmatch(
        r"Spherical position angle (latitude|longitude) angle of (\S+) w.r.t. (\S+)", id
    ):
        type, target, observer = match.groups()
        return f"{type[:3]}_{observer.lower()}"
    elif match := re.fullmatch(
        r"Single acceleration in inertial frame of type (.+), acting on (\S+), exerted by (\S+)",
        id,
    ):
        type, target, exerter = match.groups()
        if "gravity" in type:
            return f"acc_grav_{exerter.lower()}"
        elif "radiation pressure" in type:
            return f"acc_rp_{exerter.lower()}"
    elif match := re.fullmatch(r"Received irradiance at (\S+) due to (\S+)", id):
        target, source = match.groups()
        return f"irr_{source.lower()}"
    elif match := re.fullmatch(r"Received fraction of irradiance at (\S+) due to (\S+)", id):
        target, source = match.groups()
        return f"occ_{source.lower()}"
    elif match := re.fullmatch(r"Number of (.+) source panels of (\S+) as seen from (\S+)", id):
        type, source, target = match.groups()
        if type == "visible":
            return f"panels_vis_{source.lower()}"
        elif type == "illuminated":
            return f"panels_ill_{source.lower()}"
        elif type == "visible and illuminated":
            return f"panels_vis_ill_{source.lower()}"
    elif match := re.fullmatch(r"Visible area of (\S+) as seen from (\S+)", id):
        source, target = match.groups()
        return f"area_vis_{source.lower()}"

    raise Exception(f'Unknown variable id "{id}"')


def _get_number_of_columns(dependent_variable_history_file: str):
    with open(dependent_variable_history_file) as f:
        first_line = f.readline()
    return first_line.count(",") + 1


def load_simulation_results(result_dir: Union[Path, str], do_tf=False):
    if isinstance(result_dir, str):
        result_dir = Path(result_dir)

    dependent_variable_history_file = result_dir / "dependent_variable_history.csv"
    colnames = _get_column_names(result_dir)
    # Add 1 because of time index
    assert len(colnames) + 1 == _get_number_of_columns(dependent_variable_history_file)

    df = pd.read_csv(dependent_variable_history_file, names=colnames)
    df["t_et"] = df.index
    df.index = pd.to_datetime(df["t_et"].swifter.apply(lambda t: as_utc(t, sec_prec=6))).rename("t")

    if do_tf:
        df = _enhance_df(df)

    return df


def _enhance_df(df: pd.DataFrame):
    def tf(row):
        pos = row[pos_names].to_numpy()
        vel = row[vel_names].to_numpy()
        pos_sun = row[["pos_sun_x", "pos_sun_y", "pos_sun_z"]].to_numpy()

        # Find RP accelerations in RSW frame
        for source in ["sun", "moon", "mercury", "earth"]:
            if f"acc_rp_{source}_x" not in row.index:
                continue

            acc = row[[f"acc_rp_{source}_x", f"acc_rp_{source}_y", f"acc_rp_{source}_z"]].to_numpy()
            (
                row[f"acc_rp_{source}_radial"],
                row[f"acc_rp_{source}_along"],
                row[f"acc_rp_{source}_cross"],
            ) = cart2track(acc, vel, pos)

        # Find subsolar angle
        pos_unit = pos / np.linalg.norm(pos)
        pos_sun_unit = pos_sun / np.linalg.norm(pos_sun)
        row["angle_subsolar"] = np.degrees(np.arccos(np.clip(pos_unit @ pos_sun_unit, -1, 1)))

        return row

    # Find magnitudes of positions and accelerations
    df["r"] = np.sqrt(np.square(df[pos_names]).sum(axis=1))
    if "pos_sun_x" in df.columns:
        df["r_sun"] = np.sqrt(np.square(df[["pos_sun_x", "pos_sun_y", "pos_sun_z"]]).sum(axis=1))
    for acc in acc_names:
        if f"{acc}_x" in df.columns:
            df[acc] = np.sqrt(np.square(df[[f"{acc}_x", f"{acc}_y", f"{acc}_z"]]).sum(axis=1))

    # Convert latitude/longitude to degrees
    for angle in ["lat_moon", "lon_moon"]:
        if angle in df.columns:
            df[angle] = np.degrees(df[angle])

    df = df.swifter.apply(tf, axis=1)
    return df


def load_walltime_duration(result_dir: Union[Path, str]):
    if isinstance(result_dir, str):
        result_dir = Path(result_dir)

    cpu_time = pd.read_csv(result_dir / "cpu_time.csv", names=["t_sim", "t_wall"])
    walltime_propagation = cpu_time["t_wall"].iloc[-1] - cpu_time["t_wall"].iloc[0]

    walltime_file_total = result_dir / "walltime.txt"
    if walltime_file_total.exists():
        with walltime_file_total.open() as f:
            walltime_total = list(map(float, f.read().strip().split("\n")))
    else:
        walltime_total = []

    return walltime_propagation, walltime_total


def load_all_simulation_results(
    results_base: Union[Path, str], load_runs=False, do_tf=False, n_workers=1
):
    if isinstance(results_base, str):
        results_base = Path(results_base)

    result_dirs = [e for e in results_base.iterdir() if e.is_dir()]

    metadata = {}
    runs = {}

    with tqdm(total=len(result_dirs)) as pbar:
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            futures = [
                executor.submit(_load_metadata_and_run, result_dir, load_runs, do_tf)
                for result_dir in result_dirs
            ]

            for future in as_completed(futures):
                res = future.result()
                pbar.update(1)

                run_no = res[0]
                metadata[run_no] = res[1]
                if load_runs:
                    runs[run_no] = res[2]

    metadata = pd.DataFrame(metadata).T
    metadata.sort_index(inplace=True)

    runs = dict(sorted(runs.items()))

    if load_runs:
        return metadata, runs
    else:
        return metadata


def _load_metadata_and_run(result_dir, load_run, do_tf):
    """Only to be used by load_all_simulation_results()"""
    run_no = int(result_dir.name)
    with (result_dir / "settings.json").open() as f:
        metadata = json.load(f)
    metadata["walltime_propagation"], metadata["walltime_total"] = load_walltime_duration(
        result_dir
    )

    if load_run:
        run = load_simulation_results(result_dir, do_tf=do_tf)
        return run_no, metadata, run
    else:
        return run_no, metadata


def load_pickled_simulation_results(
    results_base: Path,
) -> Tuple[pd.DataFrame, dict[int, pd.DataFrame]]:
    if isinstance(results_base, str):
        results_base = Path(results_base)

    return pd.read_pickle(results_base / "results.pkl")
