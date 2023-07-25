import csv
import json
import re
from pathlib import Path
from typing import Union, Tuple

import numpy as np
import pandas as pd
# noinspection PyUnresolvedReferences
import swifter
from tqdm import tqdm

from lropy.analysis.spice_tools import as_utc
from lropy.analysis.transform import cart2track

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


def get_column_names(result_dir: Path):
    colnames = []

    with (result_dir / "dependent_variable_names.csv").open(newline="") as f:
        for var in csv.DictReader(f, delimiter=";"):
            name = _get_column_name(var["ID"])
            size = int(var["Size"])
            if size == 1:
                # Scalar
                colnames.append(name)
            else:
                # Vector
                if size == 3:
                    elements = ["x", "y", "z"]
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
    colnames = get_column_names(result_dir)
    # Add 1 because of time index
    assert len(colnames) + 1 == _get_number_of_columns(dependent_variable_history_file)

    df = pd.read_csv(dependent_variable_history_file, names=colnames)
    df["t_et"] = df.index
    df.index = pd.to_datetime(df["t_et"].swifter.apply(lambda t: as_utc(t, sec_prec=6))).rename("t")
    # df.index = pd.to_datetime(
    #     df["t_et"].swifter.apply(lambda t: as_utc(t, sec_prec=6)),
    #     format="%Y-%m-%d %H:%M:%S.%f UTC").rename("t")

    df["r"] = np.sqrt(np.square(df[pos_names]).sum(axis=1))
    if "pos_sun_x" in colnames:
        df["r_sun"] = np.sqrt(np.square(df[["pos_sun_x", "pos_sun_y", "pos_sun_z"]]).sum(axis=1))
    for acc in acc_names:
        if f"{acc}_x" in colnames:
            df[acc] = np.sqrt(np.square(df[[f"{acc}_x", f"{acc}_y", f"{acc}_z"]]).sum(axis=1))
    for angle in ["lat_moon", "lon_moon"]:
        if angle in colnames:
            df[angle] = np.degrees(df[angle])

    def tf(row):
        pos = row[pos_names].to_numpy()
        vel = row[vel_names].to_numpy()
        pos_sun = row[["pos_sun_x", "pos_sun_y", "pos_sun_z"]].to_numpy()

        for source in ["sun", "moon", "mercury", "earth"]:
            if f"acc_rp_{source}_x" not in row.index:
                continue

            acc = row[[f"acc_rp_{source}_x", f"acc_rp_{source}_y", f"acc_rp_{source}_z"]].to_numpy()
            (
                row[f"acc_rp_{source}_radial"],
                row[f"acc_rp_{source}_along"],
                row[f"acc_rp_{source}_cross"],
            ) = cart2track(acc, vel, pos)

        pos_norm = pos / np.linalg.norm(pos)
        pos_sun_norm = pos_sun / np.linalg.norm(pos_sun)

        row["angle_subsolar"] = np.degrees(np.arccos(np.clip(pos_norm @ pos_sun_norm, -1, 1)))

        return row

    if do_tf:
        # Do expensive transformations
        df = df.apply(tf, axis=1)

    return df


def load_walltime_duration(result_dir: Union[Path, str]):
    if isinstance(result_dir, str):
        result_dir = Path(result_dir)

    cpu_time = pd.read_csv(result_dir / "cpu_time.csv", names=["t_sim", "t_wall"])
    walltime = cpu_time["t_wall"]
    return walltime.iloc[-1] - walltime.iloc[0]


def load_all_simulation_results(results_base: Union[Path, str], load_runs=False, do_tf=False):
    if isinstance(results_base, str):
        results_base = Path(results_base)

    result_dirs = [e for e in results_base.iterdir() if e.is_dir()]

    metadata = {}
    runs = {}

    for result_dir in tqdm(result_dirs):
        run_no = int(result_dir.name)
        with (result_dir / "settings.json").open() as f:
            metadata[run_no] = json.load(f)
        metadata[run_no]["walltime_duration"] = load_walltime_duration(result_dir)

        if load_runs:
            runs[run_no] = load_simulation_results(result_dir, do_tf=do_tf)

    metadata = pd.DataFrame(metadata).T
    metadata.sort_index(inplace=True)

    runs = dict(sorted(runs.items()))

    if load_runs:
        return metadata, runs
    else:
        return metadata


def load_pickled_simulation_results(
    results_base: Path,
) -> Tuple[pd.DataFrame, dict[int, pd.DataFrame]]:
    if isinstance(results_base, str):
        results_base = Path(results_base)

    return pd.read_pickle(results_base / "results.pkl")
