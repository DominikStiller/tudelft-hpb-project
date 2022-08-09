import spiceypy as spice


lro_spice_base = "/home/dominik/dev/tudat-bundle/spice/lro/data"


def as_et(time):
    spice.furnsh(f"{lro_spice_base}/lsk/naif0012.tls")
    return spice.str2et(time)
