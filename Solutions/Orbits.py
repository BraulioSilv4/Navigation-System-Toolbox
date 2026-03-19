from Solutions.ReferenceCoordinate import azimuth
from common.Orbits.Ephemeris import Ephemeris, calc_dt
from common.Orbits.KeplerianOrbit import KeplerianOrbit
from common.data_components import ECEF, ENU

orbit: KeplerianOrbit = KeplerianOrbit(a=26559755, e=0.017545, omega=1.626021)

####### Exercise 1 #######

orbital_period = orbit.orbital_period()
print(f"Orbital period: {orbital_period} seconds")

mean_angular_velocity = orbit.satellite_mean_motion()
print(f"Mean angular velocity: {mean_angular_velocity} radians/second")

mean_anomaly = orbit.mean_anomaly(t=39929.0)
print(f"Mean anomaly at t=39929.0 seconds: {mean_anomaly} radians")

eanom_default, niter_default = orbit.eccentric_anomaly_default(mean_anomaly)
print(f"Eccentric anomaly (default method): {eanom_default} radians, computed in {niter_default} iterations")

eanom_raphson, niter_raphson = orbit.eccentric_anomaly_raphson(mean_anomaly)
print(f"Eccentric anomaly (Raphson method): {eanom_raphson} radians, computed in {niter_raphson} iterations")

radius, true_anom = orbit.radius_true_anomaly(eanom_raphson)
print(f"Radius at t=39929.0 seconds: {radius} meters")
print(f"True anomaly at t=39929.0 seconds: {true_anom} radians")

argument_of_latitude = orbit.argument_of_latitude(true_anom)
print(f"Argument of latitude at t=39929.0 seconds: {argument_of_latitude} radians")

########## Exercise 2 #######
eph: Ephemeris = Ephemeris(
    WN=2056, toe=540000.0, M0=-0.820, sqrt_a=5154, e=0.0076, i0=0.9827, lon0=1.143, omega=1.093, dn=0.0, dotlon=0.0,
    cuc=0.0, cus=0.0, crc=0.0, crs=0.0, cic=0.0, cis=0.0, IDOT=0.0, IODE=0
)

tow_at_perigee = eph.TOW_at_perigee_passage()
print(f"Time of week at perigee passage: {tow_at_perigee} seconds")

tow_first_perigee = eph.TOW_of_first_perigee_passage()
print(f"Time of week of first perigee passage: {tow_first_perigee} seconds")

############### Exercise 3 ###############
dt = calc_dt(wna=2057, wnb=2058, towa=600830, towb=86)
print(f"Time difference between two epochs: {dt} seconds")

############### Exercise 4 ###############
eph2: Ephemeris = Ephemeris(
    WN=8, toe=532800.0, M0=-2.185e-01, sqrt_a=5.154e03, e=1.889e-02, i0=9.552e-01, lon0=3.108e+00, omega=-1.737e+00, dn=4.869e-09, dotlon=-8.740e-09,
    cuc=0.0, cus=0.0, crc=0.0, crs=0.0, cic=0.0, cis=0.0, IDOT=4.464e-11, IODE=0
)

s = eph2.calculate_position(t=536400.0)
print(f"Satellite position at t=536400.0 seconds: {s}")

############## Exercise 5 ##############
r1: ECEF = ECEF(x=4918525.18, y=-791212.21, z=3969762.19)
r1_eph2_enu: ENU = r1.ecef_to_enu(target=s)

azi = r1_eph2_enu.azimuth()
ele = r1_eph2_enu.elevation()
print(f"Receiver position (ECEF): {r1}")
print(f"Azimuth of the satellite from the observer: {azi} deg")
print(f"Elevation of the satellite from the observer: {ele} deg")

############## Exercise 6 ##############
