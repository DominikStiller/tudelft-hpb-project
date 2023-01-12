import pandas as pd
import numpy as np


moon_polar_radius = 1736e3  # m
JULIAN_DAY = 86400.0  # s
JULIAN_DAY_ON_J2000 = 2451545.0  # s


pos_names = ["pos_x", "pos_y", "pos_z"]
acc_names = ["acc_grav_moon", "acc_grav_earth", "acc_grav_sun", "acc_rp_sun", "acc_rp_moon"]


def read_simulation_results(dependent_variable_history_file: str):
    def gen_vector_colnames(names):
        colnames = []
        for name in names:
            if "kepler" in name:
                elements = ["a", "e", "i", "longAscNode", "argPeri", "trueAnom"]
            else:
                elements = ["x", "y", "z"]
            colnames.extend([f"{name}_{elem}" for elem in elements])
        return colnames
    
    df = pd.read_csv(dependent_variable_history_file,
                         names=gen_vector_colnames(["pos", "vel", "kepler", "pos_sun"] + acc_names))
    df["t_et"] = df.index
    df.index = pd.to_datetime(df.index / JULIAN_DAY + JULIAN_DAY_ON_J2000, origin="julian", unit='D')
    
    df["r"] = np.sqrt(np.square(df[pos_names]).sum(axis=1))
    df["r_sun"] = np.sqrt(np.square(df[["pos_sun_x", "pos_sun_y", "pos_sun_z"]]).sum(axis=1))
    for acc in acc_names:
        df[acc] = np.sqrt(np.square(df[[f"{acc}_x", f"{acc}_y", f"{acc}_z"]]).sum(axis=1)) 
    
    return df

