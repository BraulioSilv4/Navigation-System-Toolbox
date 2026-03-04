from common.nmea_data_components import LLH, Coordinates, Latitude, Longitude, Altitude, ECEF, ENU
from common.nmea_enum import Hemisphere, DistanceMeasureUnit, Ellipsoids
from common.nmea_functions import distance_between

p1: LLH = LLH(
    Coordinates(
        Latitude.from_dms(degrees=38, minutes=46, seconds=49.61, lat_dir=Hemisphere.NORTH),
        Longitude.from_dms(degrees=9, minutes=29, seconds=56.19, lon_dir=Hemisphere.WEST)
    ),
    Altitude(
        value=103.0,
        unit=DistanceMeasureUnit.METERS
    )
)

print(f"""
    Latitude: DDMM.mmm = {p1.coordinates.lat.degrees}º{p1.coordinates.lat.minutes:.4f}' {p1.coordinates.lat.lat_dir.value}
    Longitude: DDDMM.mmm = {p1.coordinates.lon.degrees}º{p1.coordinates.lon.minutes:.4f}' {p1.coordinates.lon.lon_dir.value}
    
    Latitude: DD.ddd = {p1.coordinates.lat.to_dd():.4f}º
    Longitude: DDD.ddd = {p1.coordinates.lon.to_dd():.4f}º
""")


p1_ecef: ECEF = p1.llh_to_ecef(ellipsoid=Ellipsoids.WGS_84)

print(f"""
    X: {p1_ecef.x:.4f} m
    Y: {p1_ecef.y:.4f} m
    Z: {p1_ecef.z:.4f} m
""")

p2: ECEF = ECEF(x=4910384.3, y=-821478.6, z=3973549.6)
p2_llh: LLH = p2.ecef_to_llh(Ellipsoids.WGS_84)

lat_deg, lat_min, lat_sec, lat_dir = p2_llh.coordinates.lat.to_dms()
lon_deg, lon_min, lon_sec, lon_dir = p2_llh.coordinates.lon.to_dms()
print(f"""
    Format DD.ddd:
        Latitude: {p2_llh.coordinates.lat.to_dd():.4f}º
        Longitude: {p2_llh.coordinates.lon.to_dd():.4f}º
    
    Format DDDMM.mmm:
        Latitude: {p2_llh.coordinates.lat.degrees}º{p2_llh.coordinates.lat.minutes}'{p2_llh.coordinates.lat.lat_dir.value}
        Longitude: {p2_llh.coordinates.lon.degrees}º{p2_llh.coordinates.lon.minutes}'{p2_llh.coordinates.lon.lon_dir.value}
        
    Format DDMMSS.ss:
        Latitude: {lat_deg}º{lat_min}'{lat_sec:.2f}" {lat_dir.value}
        Longitude: {lon_deg}º{lon_min}'{lon_sec:.2f}" {lon_dir.value}
""")


dist_p1_p2 = distance_between(p1, p2)

print(f"Distance between p1 and p2: {dist_p1_p2:.4f} m")

enu_p1_p2: ENU = p1_ecef.ecef_to_enu(p2)

print(f"""
    ENU coordinates of p2 relative to p1:
    East: {enu_p1_p2.e:.4f} m
    North: {enu_p1_p2.n:.4f} m
    Up: {enu_p1_p2.u:.4f} m
""")

azimuth = enu_p1_p2.azimuth()
elevation = enu_p1_p2.elevation()

print(f"""
    Azimuth from p1 to p2: {azimuth:.4f}º
    Elevation from p1 to p2: {elevation:.4f}º
""")