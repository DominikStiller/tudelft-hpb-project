import csv
import json
from pathlib import Path
from typing import Union

import pandas as pd
import numpy as np
from tqdm import tqdm
import swifter

from spice_tools import as_utc
from util import cart2track, cart2spher


pos_names = ["pos_x", "pos_y", "pos_z"]
vel_names = ["vel_x", "vel_y", "vel_z"]
acc_names = [
    "acc_grav_moon",
    "acc_grav_earth",
    "acc_grav_sun",
    "acc_rp_sun",
    "acc_rp_moon",
    "acc_rp_earth",
]
irr_names = ["irr_sun", "irr_moon"]
panels_count_names = ["panels_vis_moon", "panels_ill_moon", "panels_vis_ill_moon"]

dependent_variable_names = {
    "Relative position of LRO w.r.t. Moon": "pos",
    "Relative position of Vehicle w.r.t. Earth": "pos",
    "Relative velocity of LRO w.r.t. Moon": "vel",
    "Relative velocity of Vehicle w.r.t. Earth": "vel",
    "Kepler elements of LRO w.r.t. Moon": "kepler",
    "Altitude of LRO w.r.t. Moon": "h",
    "Relative position of Sun w.r.t. Moon": "pos_sun",
    "Single acceleration in inertial frame of type spherical harmonic gravity , acting on LRO, exerted by Moon": "acc_grav_moon",
    "Single acceleration in inertial frame of type spherical harmonic gravity , acting on LRO, exerted by Earth": "acc_grav_earth",
    "Single acceleration in inertial frame of type central gravity , acting on LRO, exerted by Sun": "acc_grav_sun",
    "Single acceleration in inertial frame of type radiation pressure acceleration, acting on LRO, exerted by Sun": "acc_rp_sun",
    "Single acceleration in inertial frame of type cannonball radiation pressure , acting on LRO, exerted by Sun": "acc_rp_sun",
    "Single acceleration in inertial frame of type panelled radiation pressure acceleration , acting on LRO, exerted by Sun": "acc_rp_sun",
    "Single acceleration in inertial frame of type radiation pressure acceleration, acting on Vehicle, exerted by Earth": "acc_rp_earth",
    "Received irradiance at LRO due to Sun": "irr_sun",
    "Received fraction of irradiance at LRO due to Sun": "occ_sun",
    "Single acceleration in inertial frame of type radiation pressure acceleration, acting on LRO, exerted by Moon": "acc_rp_moon",
    "Received irradiance at LRO due to Moon": "irr_moon",
    "Number of visible source panels of Moon as seen from LRO": "panels_vis_moon",
    "Number of illuminated source panels of Moon as seen from LRO": "panels_ill_moon",
    "Number of visible and illuminated source panels of Moon as seen from LRO": "panels_vis_ill_moon",
    "Visible area of Earth as seen from Vehicle": "area_vis_earth",
    "Visible area of Moon as seen from LRO": "area_vis_moon",
}


def get_column_names(result_dir: Path):
    colnames = []

    with (result_dir / "dependent_variable_names.csv").open(newline="") as f:
        for var in csv.DictReader(f, delimiter=";"):
            name = dependent_variable_names[var["ID"]]
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
    df.index = pd.to_datetime(
        df["t_et"].swifter.apply(lambda t: as_utc(t, sec_prec=6))
    ).rename("t")
    # df.index = pd.to_datetime(
    #     df["t_et"].swifter.apply(lambda t: as_utc(t, sec_prec=6)),
    #     format="%Y-%m-%d %H:%M:%S.%f UTC").rename("t")

    df["r"] = np.sqrt(np.square(df[pos_names]).sum(axis=1))
    if "pos_sun_x" in colnames:
        df["r_sun"] = np.sqrt(
            np.square(df[["pos_sun_x", "pos_sun_y", "pos_sun_z"]]).sum(axis=1)
        )
    for acc in acc_names:
        if f"{acc}_x" in colnames:
            df[acc] = np.sqrt(
                np.square(df[[f"{acc}_x", f"{acc}_y", f"{acc}_z"]]).sum(axis=1)
            )

    def tf(row):
        pos = row[pos_names].to_numpy()
        vel = row[vel_names].to_numpy()
        pos_sun = row[["pos_sun_x", "pos_sun_y", "pos_sun_z"]].to_numpy()

        for source in ["sun", "moon"]:
            if f"acc_rp_{source}_x" not in row.index:
                continue

            acc = row[
                [f"acc_rp_{source}_x", f"acc_rp_{source}_y", f"acc_rp_{source}_z"]
            ].to_numpy()
            (
                row[f"acc_rp_{source}_radial"],
                row[f"acc_rp_{source}_along"],
                row[f"acc_rp_{source}_cross"],
            ) = cart2track(acc, vel, pos)

        pos_spher = cart2spher(*pos)
        row["lat"] = np.degrees(np.pi / 2 - pos_spher[1])
        row["lon"] = np.degrees(pos_spher[2])

        pos_norm = pos / np.linalg.norm(pos)
        pos_sun_norm = pos_sun / np.linalg.norm(pos_sun)

        row["angle_subsolar"] = np.degrees(
            np.arccos(np.clip(pos_norm @ pos_sun_norm, -1, 1))
        )

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


def load_all_simulation_results(results_base: Path, load_runs=False, do_tf=False):
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
