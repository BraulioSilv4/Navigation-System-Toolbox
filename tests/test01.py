from typing import Callable, List

from common.nmea_data_components import Coordinates, LLH, ECEF, ENU
from common.nmea_data_manager import NMEAManager
from common.nmea_enum import NMEAType
from common.nmea_functions import distance_between
from common.nmea_instance import NMEAInstance

path = r"../data/trackWA1_2025-2026.nmea"

manager: NMEAManager = NMEAManager()

# Parsing all the sentences in the file and adding them to the manager
with open(path, "r", encoding="utf-8") as f:
    for line in f:
        instance = NMEAInstance(line)
        manager.add_instance(instance)
        instance.parse()

    print("Finished parsing sentences.")
    print("\n")


    # This condition is used to obtains only the valid GGA instances. Checks Checksum, fix quality. (See NMEAInstance class)
    cond: Callable = lambda x: x.valid == True and x.data.fix_quality.value is not None and x.data.fix_quality.value not in [0, 6, 7, 8]

    print("##################### EXERCISE 2.a #####################")
    first_gga_instance = manager.get_instances_by_type(NMEAType.GGA)[0]
    coord1: Coordinates = first_gga_instance.data.coordinates
    lat1_deg, lat1_min, lat1_sec, lat1_dir = coord1.lat.to_dms()
    lon1_deg, lon1_min, lon1_sec, lon1_dir = coord1.lon.to_dms()
    print(f"First GGA instance coordinates: {lat1_deg}º{lat1_min}'{lat1_sec:.2f}\" {lat1_dir.value}, {lon1_deg}º{lon1_min}'{lon1_sec:.2f}\" {lon1_dir.value}")
    print("##################### EXERCISE 2.a END #####################\n")

    print("##################### EXERCISE 2.b #####################")
    p1_llh: LLH = LLH(coord1, first_gga_instance.data.altitude)
    p1_ecef: ECEF = p1_llh.llh_to_ecef()
    print(f"First GGA instance ECEF coordinates: X={p1_ecef.x:.4f} m, Y={p1_ecef.y:.4f} m, Z={p1_ecef.z:.4f} m")
    print("###################### EXERCISE 2.b END #####################\n")

    print("###################### EXERCISE 2.c #####################")
    last_gga_instance = manager.get_instances_by_type(NMEAType.GGA)[-1]
    coord2: Coordinates = last_gga_instance.data.coordinates

    p2_llh: LLH = LLH(coord2, last_gga_instance.data.altitude)
    p2_ecef: ECEF = p2_llh.llh_to_ecef()

    print(f"Last GGA instance coordinates: {coord2.lat.to_dd():.4f}º {coord2.lat.lat_dir.value}, {coord2.lon.to_dd():.4f}º {coord2.lon.lon_dir.value}")
    print(f"Last GGA instance ECEF coordinates: X={p2_ecef.x:.4f} m, Y={p2_ecef.y:.4f} m, Z={p2_ecef.z:.4f} m")

    enu: ENU = p1_ecef.ecef_to_enu(p2_ecef)

    print(f"ENU coordinates of last GGA instance relative to first GGA instance: E={enu.e:.4f} m, N={enu.n:.4f} m, U={enu.u:.4f} m")
    print(f"Azimuth: {enu.azimuth():.4f}º, Elevation: {enu.elevation():.4f}º")
    print("####################### EXERCISE 2.c END #####################\n")


    print("##################### EXERCISE 2.d #####################")
    lowest_altitude = min(manager.get_instances_by_type(NMEAType.GGA, cond), key=lambda x: x.data.altitude.value)
    print(f"Lowest altitude: {lowest_altitude.data.altitude.value:.4f} m at coordinates {lowest_altitude.data.coordinates.lat.to_dd():.4f}º {lowest_altitude.data.coordinates.lat.lat_dir.value}, {lowest_altitude.data.coordinates.lon.to_dd():.4f}º {lowest_altitude.data.coordinates.lon.lon_dir.value}")
    print(f"Raw sentence for lowest altitude instance: {lowest_altitude.nmea_str}")
    print(f"UTC time for lowest altitude instance: {lowest_altitude.data.utc}")
    print("###################### EXERCISE 2.d END #####################\n")


    print("###################### EXERCISE 2.e #####################")
    valid_gga_instances = manager.get_instances_by_type(NMEAType.GGA, cond)
    valid_gga_llh = [LLH(i.data.coordinates, i.data.altitude) for i in valid_gga_instances]
    valid_gga_ecef: List[ECEF] = [llh.llh_to_ecef() for llh in valid_gga_llh]

    total_distance = 0.0
    for i in range(1, len(valid_gga_ecef)):
        total_distance += distance_between(valid_gga_ecef[i-1], valid_gga_ecef[i])

    print(f"Number of valid GGA instances: {len(valid_gga_instances)}")
    print(f"Total distance traveled according to valid GGA instances: {total_distance:.4f} m")
    print("###################### EXERCISE 2.e END ####################\n")




    # Extra for checking
    valid = NMEAInstance("$GPRMC,153000.000,A,3844.2226,N,00908.1865,W,1.75,162.40,050326,,,A*F7")
    valid.parse()
    print(f"Parsing test sentence: Valid={valid.valid}")

