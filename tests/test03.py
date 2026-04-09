from typing import Tuple, List

import numpy as np

from common.Orbits.Ephemeris import Ephemeris
from common.Orbits.ephemeris_parser import EphemerisParser
from common.data_components import ECEF, PDOP, HDOP, GDOP
from common.functions import LS
from common.nprParser import nprParser, NPRData

r1: ECEF = ECEF(4918532, -791213, 3969755)

# Exercise 1
eph_parser = EphemerisParser(file="../data/ns2025-2026_WA3.eph")
sats: List[Tuple[int, Ephemeris]] = eph_parser.parse()
sats_above_10_deg = []

H_matrix = []
for svn, eph in sats:
    pos_at_tx, niter = eph.sat_position_at_tx(r=r1, t_rx=(640800 - eph.toe + 24))  # WN=2057 and TOW=24s
    enu = r1.ecef_to_enu(target=pos_at_tx)
    cosines = r1.ecef_to_direction_cosines(target=pos_at_tx)
    elevation = enu.elevation()
    if elevation > 10:
        sats_above_10_deg.append(eph)
        s_j = pos_at_tx.to_vector()
        r = r1.to_vector()
        dist = np.linalg.norm(s_j - r)
        e_j = (s_j - r) / dist
        H_matrix.append(np.append(-e_j, 1.0))
        print(f"SVN{svn}: Coordinates {pos_at_tx}, direction cosines {cosines}")


H_1 = np.array(H_matrix)
r1_rot = r1.ecef_to_llh().to_rotation()
hthinv = np.linalg.inv(H_1.T @ H_1)
hthinv_enu = r1_rot @ hthinv[:3, :3] @ r1_rot.T

hdop = HDOP(hthinv_enu)
gdop = GDOP(hthinv)
print(f"H matrix:\n{np.array(H_matrix)}")
print(f"HDOP: {hdop:.4f}")
print(f"GDOP: {gdop:.4f}")

# Exercise 2
npr_data: list[NPRData] = nprParser("../data/ns2025-2026_WA3.pr")
pseudo_ranges: list[float] = [npr.pseudoranges[0] for npr in npr_data]  # Pseudoranges for the first epoch (t=604800 + 24 seconds)
for i, pseudo_range in enumerate(pseudo_ranges):
    j = i + 1
    if j in [1, 2, 5, 7, 10]:
        pseudo_ranges.append(pseudo_range)

prange_sats: list[tuple[float, Ephemeris]] = list(zip(pseudo_ranges, sats_above_10_deg))
position, estimate, H, niter = LS(guess=r1, prange_sats=prange_sats, trx=24, max_iter=1, debug=True)
print(f"H matrix after 1 iteration:\n{H}")
print(f"Receiver position estimate: {position}, clock bias: {estimate:.4f} m")

#convert clock bias in meters to seconds
clock_bias_seconds = estimate / 299792458.0
print(f"Receiver clock bias: {clock_bias_seconds:.9f} seconds")

# Exercise 2.b
# gps time scale
gps_time_seconds = 604800 + 24 + clock_bias_seconds
print(f"GPS time at reception: {gps_time_seconds:.9f} seconds")