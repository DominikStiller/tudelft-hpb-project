import numpy as np


def spher2cart(radius, polar, azimuth):
    # u=azimuth, v=polar
    x = radius * np.cos(azimuth) * np.sin(polar)
    y = radius * np.sin(azimuth) * np.sin(polar)
    z = radius * np.cos(polar)

    return x, y, z


def cart2spher(x, y, z):
    radius = np.linalg.norm([x, y, z])
    polar = np.arccos(z / radius)
    azimuth = np.arctan2(y, x)

    return radius, polar, azimuth


def cart2track(acc, vel, pos):
    radialUnit = pos / np.linalg.norm(pos)
    alongTrackUnit = vel - radialUnit * (vel @ radialUnit)
    alongTrackUnit /= np.linalg.norm(alongTrackUnit)
    crossTrackUnit = np.cross(radialUnit, alongTrackUnit)
    crossTrackUnit /= np.linalg.norm(crossTrackUnit)

    return acc.dot(radialUnit), acc.dot(alongTrackUnit), acc.dot(crossTrackUnit)


def align_vectors(from_vec, to_vec):
    # From https://stackoverflow.com/a/67767180
    a, b = (from_vec / np.linalg.norm(from_vec)).reshape(3), (
        to_vec / np.linalg.norm(to_vec)
    ).reshape(3)
    v = np.cross(a, b)
    if any(v):  # if not all zeros then
        c = np.dot(a, b)
        s = np.linalg.norm(v)
        kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        return np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s**2))
    else:
        return np.eye(3)  # cross of all zeros only occurs on identical directions
