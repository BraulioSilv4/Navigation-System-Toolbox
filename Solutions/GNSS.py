from typing import List, Tuple

import numpy as np

from common.Orbits.Ephemeris import Ephemeris
from common.Orbits.ephemeris_parser import EphemerisParser
from common.data_components import ECEF, PDOP

r1: ECEF = ECEF(x=4918525.18, y=-791212.21, z=3969762.19)
s10: ECEF = ECEF(x=-5845119.0, y=-14047494.0, z=21837689.0)

# Exercise 1
true_range = r1.range(s10)
print(f"True range between observer and satellite: {true_range:.4f} m")

pseudorange = r1.pseudorange(s10, offset=500e-6)
print(f"Pseudorange between observer and satellite with 500 microseconds offset: {pseudorange:.4f} m")


# Exercise 2
# a) z -> 8x1
# b) H -> 8x2
# c) x -> 2x1
# d) H^T -> 2x8
# e) H^T * H -> 2x2
# f) (H^T * H)^-1 -> 2x2
# g) (H^T * H)^-1 * H^T -> 2x1

# Exercise 3
hthinv = np.array([[1.108, -0.148, 0.491, 0.608], [-0.148, 0.386, 0.165, -0.011], [0.491, 0.165, 1.152, 0.590], [0.608, -0.011, 0.590, 0.570]])
pdop = PDOP(hthinv)
print(pdop)

# Exercise 4
eph_parser: EphemerisParser = EphemerisParser(file="../data/ub1.ubx.2056.540000b.eph")
orb: List[Tuple[int, Ephemeris]] = eph_parser.parse()

dict_svn_range = {}
start = 536400
for i in range(3600):
    for svn, eph in orb:
        pos_at_tx, niter = eph.sat_position_at_tx(r=r1, t_rx=start + i)
        enu = r1.ecef_to_enu(target=pos_at_tx)
        elevation = enu.elevation()
        if elevation > 10.0:
            true_range = r1.range(pos_at_tx)
            dict_svn_range[svn] = dict_svn_range.get(svn, []) + [true_range]

# plot the ranges for each satellite
import matplotlib.pyplot as plt

for svn, range_ in dict_svn_range.items():
    plt.plot(range_, label=f'SVN {svn}')
    plt.xlabel('Time (s)')
    plt.ylabel('Range (m)')
    plt.title('Range to Satellites Over Time')
    plt.legend()
    plt.grid()
    plt.show()