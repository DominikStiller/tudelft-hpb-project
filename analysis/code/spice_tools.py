import numpy as np
import pandas as pd
import spiceypy as spice
import spiceypy.utils.support_types as stypes
import glob


lro_spice_base = "/home/dominik/dev/tudat-bundle/spice/lro/data"

TDBFMT = 'YYYY-MM-DD HR:MN:SC.### TDB ::TDB'

JULIAN_DAY = 86400.0  # s
JULIAN_DAY_ON_J2000 = 2451545.0  # s


def generate_lro_ephemeris(timestamps):
    for file in glob.glob(f"{lro_spice_base}/spk/*.bsp"):
        spice.furnsh(file)
    spice.furnsh(f"{lro_spice_base}/lsk/naif0012.tls")
    
    ephemeris = spice.spkezr("LRO", timestamps, "ECLIPJ2000", "NONE", "Moon")[0]
    spice.kclear()
    
    colnames = ["pos_x", "pos_y", "pos_z", "vel_x", "vel_y", "vel_z"]
    
    df = pd.DataFrame(ephemeris, index=timestamps, columns=colnames)
    df["t_et"] = df.index
    df[colnames] *= 1e3
    df.index = pd.to_datetime(df.index / JULIAN_DAY + JULIAN_DAY_ON_J2000, origin="julian", unit='D').rename("t")
    
    df["r"] = np.sqrt(np.square(df[["pos_x", "pos_y", "pos_z"]]).sum(axis=1))
    
    return df


def calculate_eclipses(occulted, occulting, observer, start, stop):
    for file in glob.glob(f"{lro_spice_base}/spk/*.bsp"):
        spice.furnsh(file)
    spice.furnsh(f"{lro_spice_base}/lsk/naif0012.tls")
    spice.furnsh(f"{lro_spice_base}/pck/pck00010.tpc")
    
    stepsize = 300.0
    
    if isinstance(start, str):
        start = spice.str2et(start)
    if isinstance(stop, str):
        stop = spice.str2et(stop)
    
    confine = stypes.SPICEDOUBLE_CELL(2)
    spice.wninsd( start, stop, confine)

    occultations = []
    for occ_type in ["FULL", "ANNULAR", "PARTIAL"]:
        occultation_windows = stypes.SPICEDOUBLE_CELL(10000)
        spice.gfoclt( occ_type,
                     occulting,    "ellipsoid",  f"iau_{occulting}",
                        occulted,     "ellipsoid",  f"iau_{occulted}",
                         "none", observer,  stepsize, confine, occultation_windows)

        for i in range(spice.wncard( occultation_windows )):
            [intbeg, intend] = spice.wnfetd(occultation_windows, i)
            occultations.append((intbeg, intend, occ_type))
    occultations.sort()

    spice.kclear()
    
    return occultations


def as_et(time):
    spice.furnsh(f"{lro_spice_base}/lsk/naif0012.tls")
    return spice.str2et(time)


def as_tdb(time):
    spice.furnsh(f"{lro_spice_base}/lsk/naif0012.tls")
    return spice.timout(time, TDBFMT)
