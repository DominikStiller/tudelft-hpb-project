import pandas as pd
import numpy as np


moon_polar_radius = 1736e3  # m
JULIAN_DAY = 86400.0  # s
JULIAN_DAY_ON_J2000 = 2451545.0  # s


pos_names = ["pos_x", "pos_y", "pos_z"]
acc_names = ["acc_grav_moon", "acc_grav_earth", "acc_grav_sun", "acc_rp_sun", "acc_rp_moon"]
irr_names = ["irr_sun", "irr_moon"]
panels_count_names = ["panels_vis_moon", "panels_ill_moon", "panels_vis_ill_moon"]
dep_var_names = ["pos", "vel", "kepler", "pos_sun"] + acc_names + irr_names + \
    ["occ_sun"] + panels_count_names


def _get_dependent_variable_elements(name: str) -> list[str]:
    if "kepler" in name:
        return ["a", "e", "i", "longAscNode", "argPeri", "trueAnom"]
    elif "acc" in name or "vel" in name or "pos" in name:
        return ["x", "y", "z"]
    else:
        return None


def _get_number_of_columns(dependent_variable_history_file: str):
    with open(dependent_variable_history_file) as f:
        first_line = f.readline()
    return first_line.count(",") + 1


def read_simulation_results(dependent_variable_history_file: str):
    def gen_vector_colnames(names):
        colnames = []
        for name in names:
            elements = _get_dependent_variable_elements(name)
            if elements:
                colnames.extend([f"{name}_{elem}" for elem in elements])
            else:
                colnames.append(name)
        return colnames
    
    colnames = gen_vector_colnames(dep_var_names)
    # Add 1 because of time index
    assert len(colnames) + 1 == _get_number_of_columns(dependent_variable_history_file)

    df = pd.read_csv(dependent_variable_history_file, names=colnames)
    df["t_et"] = df.index
    df.index = pd.to_datetime(df.index / JULIAN_DAY + JULIAN_DAY_ON_J2000, origin="julian", unit='D')
    
    df["r"] = np.sqrt(np.square(df[pos_names]).sum(axis=1))
    df["r_sun"] = np.sqrt(np.square(df[["pos_sun_x", "pos_sun_y", "pos_sun_z"]]).sum(axis=1))
    for acc in acc_names:
        df[acc] = np.sqrt(np.square(df[[f"{acc}_x", f"{acc}_y", f"{acc}_z"]]).sum(axis=1)) 
    
    return df
