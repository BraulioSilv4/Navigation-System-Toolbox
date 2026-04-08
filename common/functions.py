import math
from typing import Union

import numpy as np

from common.Orbits.Ephemeris import Ephemeris
from common.data_components import LLH, ECEF
from common.NMEA.nmea_enum import Ellipsoids

WGS84_OMEGA_E = 7.2921151467e-5
c = 299792458.0

def distance_between(this: Union[LLH, ECEF], target: Union[LLH, ECEF], ellipsoid: Ellipsoids) -> float:
    src: ECEF
    dst: ECEF

    if isinstance(this, LLH):
        src = this.llh_to_ecef(source=ellipsoid)
    else:
        src = this

    if isinstance(target, LLH):
        dst = target.llh_to_ecef(source=ellipsoid)
    else:
        dst = target

    return math.sqrt(pow(dst.x - src.x, 2) + pow(dst.y - src.y, 2) + pow(dst.z - src.z, 2))


def LS(guess: ECEF, prange_sats: list[tuple[float, Ephemeris]], trx, max_iter: int = 10, debug: bool = False):
    r = guess.to_vector()
    estimate: np.ndarray = np.zeros((4, 1))

    for i in range(max_iter):
        H = []
        z = []

        if debug:
            print(f"Iteration {i + 1}:")
            print(f"Current guess for receiver position: X={r[0]:.4f} m, Y={r[1]:.4f} m, Z={r[2]:.4f} m")
        for prange, sat in prange_sats:
            sat_pos_raw, _ = sat.sat_position_at_tx(r=ECEF(r[0], r[1], r[2]), t_rx=trx, debug=debug)
            s_j = sat_pos_raw.to_vector()

            dist = np.linalg.norm(s_j - r)
            if debug:
                print(f"Distance between receiver and satellite: {dist:.4f} m")

            e_j = (s_j - r) / dist

            H.append(np.append(-e_j, 1.0))
            z.append(prange - (e_j @ s_j))

        H = np.array(H)
        z = np.array(z).reshape(-1, 1)

        estimate = np.linalg.inv(H.T @ H) @ H.T @ z

        r_new = estimate[:3].flatten()

        if np.linalg.norm(r_new - r) < 0.001:
            return ECEF(r_new[0], r_new[1], r_new[2]), estimate[3][0], H

        r = r_new

    return ECEF(r[0], r[1], r[2]), estimate[3][0], H
