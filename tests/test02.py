from typing import Tuple, List


from common.NMEA.nmea_enum import DistanceMeasureUnit, Hemisphere
from common.Orbits.Ephemeris import Ephemeris, gravitational_constant
from common.Orbits.ephemeris_parser import EphemerisParser
from common.data_components import LLH, Coordinates, Latitude, Longitude, Altitude, ECEF

eph_parser: EphemerisParser = EphemerisParser(file="../data/ns2025-2026_WA2.eph")
orbits1: List[Tuple[int, Ephemeris]] = eph_parser.parse()

############ Exercise 1 ##############
origin_llh: LLH = LLH(
    coordinates=Coordinates(
        Latitude.from_dms(37, 44.0, 20.0, Hemisphere.NORTH),
        Longitude.from_dms(25, 39.0, 10.0, Hemisphere.WEST)
    ),
    altitude=Altitude(0.0, DistanceMeasureUnit.METERS))

destiny_llh: LLH = LLH(
    coordinates=Coordinates(
        Latitude.from_dms(0, 22.0, 25.0, Hemisphere.SOUTH),
        Longitude.from_dms(48, 7.0, 35.0, Hemisphere.WEST)
    ),
    altitude=Altitude(0.0, DistanceMeasureUnit.METERS)
)

r: float  = 6371.0

distance, bearing = origin_llh.loxodrome(destiny_llh, radius=r)
print(f"Distance between origin and destiny: {distance:.4f} km")
print(f"Bearing from origin to destiny: {bearing:.4f}º")

##### Exercise 5.a ########
r: ECEF = ECEF(x=4918532, y=-791212.0, z=3969754.0)
svn2: Ephemeris = orbits1[1][1]

s_1 = svn2.calculate_position(604790)
print(f"Satellite position at t=604790s: X={s_1.x:.4f} m, Y={s_1.y:.4f} m, Z={s_1.z:.4f} m")

s_2 = svn2.calculate_position(604810)
print(f"Satellite position at t=604810s: X={s_2.x:.4f} m, Y={s_2.y:.4f} m, Z={s_2.z:.4f} m")

##### Exercise 5.b ######
distance = ((s_2.x - s_1.x)**2 + (s_2.y - s_1.y)**2 + (s_2.z - s_1.z)**2)**0.5
avg_speed = distance / 20.0
print(f"Average speed of the satellite between t=604790s and t=604810s: {avg_speed:.4f} m/s")

#### Exercise 5.c ######
svn2_at_tx, niter = svn2.sat_position_at_tx(r=r, t_rx=604790)
print(f"Satellite position at transmission time: X={svn2_at_tx.x:.4f} m, Y={svn2_at_tx.y:.4f} m, Z={svn2_at_tx.z:.4f} m, computed in {niter} iterations")

#### Exercise 5.d ######
dir_cos = r.ecef_to_direction_cosines(target=svn2_at_tx)
print(f"Direction cosines of the satellite from the observer at transmission time: {dir_cos}")