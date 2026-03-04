from common.nmea_data_components import LLH, Coordinates, Latitude, Longitude, Altitude
from common.nmea_data_manager import NMEAManager
from common.nmea_enum import Hemisphere, DistanceMeasureUnit, Ellipsoids
from common.nmea_instance import NMEAInstance

path = r"../data/ISTShuttle.nmea"

manager: NMEAManager = NMEAManager()

with open(path, "r", encoding="utf-8") as f:
    for line in f:
        instance = NMEAInstance(line)
        manager.add_instance(instance)

coord: LLH = LLH(
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
    Latitude: DDMM.mmm = {coord.coordinates.lat.degrees}º{coord.coordinates.lat.minutes:.4f}' {coord.coordinates.lat.lat_dir.value}
    Longitude: DDDMM.mmm = {coord.coordinates.lon.degrees}º{coord.coordinates.lon.minutes:.4f}' {coord.coordinates.lon.lon_dir.value}
    
    Latitude: DD.ddd = {coord.coordinates.lat.to_dd():.4f}º
    Longitude: DDD.ddd = {coord.coordinates.lon.to_dd():.4f}º
""")


x,y,z = coord.llh_to_xyz(ellipsoid=Ellipsoids.WGS_84)

print(f"""
    X: {x:.4f} m
    Y: {y:.4f} m
    Z: {z:.4f} m
""")

