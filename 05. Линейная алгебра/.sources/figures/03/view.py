"""Choice of the camera for the 3D figures of topic 03: the view in which no key direction is squashed in the picture."""
import numpy as np
from PIL import Image, ImageChops


def trim(path, margin=12):
    """Crop the white margins of the saved picture: a 3D axes keeps empty room around the scene."""
    img = Image.open(path).convert("RGB")
    box = ImageChops.difference(img, Image.new("RGB", img.size, (255, 255, 255))).getbbox()
    if box:
        l, t, r, b = box
        img.crop((max(l - margin, 0), max(t - margin, 0), min(r + margin, img.width), min(b + margin, img.height))).save(path)


def screen_axes(elev, azim):
    """Unit vectors of the picture's right and up directions for matplotlib's view_init(elev, azim)."""
    e, a = np.radians(elev), np.radians(azim)
    right = np.array([-np.sin(a), np.cos(a), 0.0])
    up = np.array([-np.sin(e) * np.cos(a), -np.sin(e) * np.sin(a), np.cos(e)])
    return right, up


def camera(elev, azim):
    """Unit vector from the scene to the camera."""
    e, a = np.radians(elev), np.radians(azim)
    return np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])


def best_view(vectors, normals=(), pairs=(), elev_range=(14, 38), azim_range=(-85, -15)):
    """(elev, azim) maximising the smallest ratio of a vector's length in the picture to its true length.

    A plane with the normal n stays readable only if the camera is neither edge-on nor face-on to it,
    so views with |n . camera| outside [0.35, 0.85] are skipped. For every pair (a, b) the score also
    counts the area of their picture parallelogram relative to the true one, so two drawn arrows
    do not collapse onto one line.
    """
    unit = [np.asarray(v, float) / np.linalg.norm(v) for v in vectors]
    unit_normals = [np.asarray(n, float) / np.linalg.norm(n) for n in normals]
    best, best_score = None, -1.0
    for elev in range(elev_range[0], elev_range[1] + 1, 2):
        for azim in range(azim_range[0], azim_range[1] + 1, 2):
            c = camera(elev, azim)
            if any(not 0.35 <= abs(n @ c) <= 0.85 for n in unit_normals):
                continue
            r, u = screen_axes(elev, azim)
            score = min(np.hypot(v @ r, v @ u) for v in unit)
            for a, b in pairs:
                a, b = np.asarray(a, float), np.asarray(b, float)
                area = abs((a @ r) * (b @ u) - (a @ u) * (b @ r)) / (np.linalg.norm(a) * np.linalg.norm(b))
                score = min(score, 1.6 * area)
            if score > best_score:
                best, best_score = (elev, azim), score
    assert best is not None, "no view satisfies the plane constraints"
    return best
