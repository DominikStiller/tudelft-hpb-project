import os
import glob

import numpy as np
import pandas as pd
import spiceypy as spice
import spiceypy.utils.support_types as stypes

from lropy.constants import moon_polar_radius


if os.getenv("HOSTNAME") == "eudoxos":
    lro_spice_base = "/home2/dominik/dev/tudat-bundle/spice/lro/data"
else:
    lro_spice_base = "/home/dominik/dev/tudat-bundle/spice/lro/data"


def init_spice():
    spice.kclear()

    spice.furnsh(f"{lro_spice_base}/lsk/naif0012.tls")
    spice.furnsh(f"{lro_spice_base}/pck/pck00010.tpc")
    spice.furnsh(f"{lro_spice_base}/fk/moon_080317.tf")
    spice.furnsh(f"{lro_spice_base}/pck/moon_pa_de421_1900_2050.bpc")
    spice.furnsh(f"{lro_spice_base}/fk/lro_frames_2012255_v02.tf")
    spice.furnsh(f"{lro_spice_base}/sclk/lro_clkcor_2022075_v00.tsc")

    for file in glob.glob(f"{lro_spice_base}/spk/*.bsp"):
        spice.furnsh(file)
    for file in glob.glob(f"{lro_spice_base}/ck/*.bc"):
        spice.furnsh(file)


init_spice()


def generate_lro_ephemeris(timestamps):
    ephemeris = spice.spkezr("LRO", timestamps, "ECLIPJ2000", "NONE", "Moon")[0]

    colnames = ["pos_x", "pos_y", "pos_z", "vel_x", "vel_y", "vel_z"]

    df = pd.DataFrame(ephemeris, index=timestamps, columns=colnames)
    df["t_et"] = df.index
    df[colnames] *= 1e3
    df.index = pd.to_datetime(df["t_et"].apply(lambda t: as_utc(t, sec_prec=6))).rename("t")

    df["r"] = np.sqrt(np.square(df[["pos_x", "pos_y", "pos_z"]]).sum(axis=1))
    df["h"] = df["r"] - moon_polar_radius

    return df


def get_lro_orbital_plane_normal(t):
    pos1 = spice.spkezr("LRO", t, "ECLIPJ2000", "NONE", "Moon")[0][3:]
    # Quarter of a period later
    pos2 = spice.spkezr("LRO", t + 113 * 60 / 4, "ECLIPJ2000", "NONE", "Moon")[0][3:]
    normal = np.cross(pos1, pos2)
    return normal / np.linalg.norm(normal)


def get_lro_beta_angle(t):
    normal = get_lro_orbital_plane_normal(t)

    sun_pos = spice.spkezr("Sun", t, "ECLIPJ2000", "NONE", "Moon")[0][:3]
    sun_dir = sun_pos / np.linalg.norm(sun_pos)

    beta_angle = np.degrees(np.arccos(sun_dir @ normal)) - 90
    return beta_angle


def get_frame(body):
    if body == "Moon":
        return "MOON_PA"
    else:
        return f"IAU_{body}"


def calculate_eclipses(occulted, occulting, observer, start, stop):
    stepsize = 300.0

    if isinstance(start, str):
        start = spice.str2et(start)
    if isinstance(stop, str):
        stop = spice.str2et(stop)

    confine = stypes.SPICEDOUBLE_CELL(2)
    spice.wninsd(start, stop, confine)

    occultations = []
    for occ_type in ["FULL", "ANNULAR", "PARTIAL"]:
        occultation_windows = stypes.SPICEDOUBLE_CELL(10000)
        spice.gfoclt(
            occ_type,
            occulting,
            "ellipsoid",
            get_frame(occulting),
            occulted,
            "ellipsoid",
            get_frame(occulted),
            "none",
            observer,
            stepsize,
            confine,
            occultation_windows,
        )

        for i in range(spice.wncard(occultation_windows)):
            [intbeg, intend] = spice.wnfetd(occultation_windows, i)
            occultations.append((intbeg, intend, occ_type))
    occultations.sort()

    return occultations


def rotate_frame(from_frame, to_frame, time):
    return spice.pxform(from_frame, to_frame, time)


def as_et(time):
    return spice.str2et(time)


def as_utc(time, sec_prec=0):
    sec_fmt = ""
    if sec_prec > 0:
        sec_fmt = "." + sec_prec * "#"

    return spice.timout(time, f"YYYY-MM-DD HR:MN:SC{sec_fmt} UTC ::UTC")


def as_tdb(time):
    return spice.timout(time, "YYYY-MM-DD HR:MN:SC TDB ::TDB")
