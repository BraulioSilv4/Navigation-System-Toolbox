from datetime import time, date

from common.data_components import Coordinates, Latitude, Longitude, Altitude, SatelliteInfo
from common.NMEA.nmea_enum import Hemisphere, FixQuality, DistanceMeasureUnit, StatusIndicator, ModeIndicator, FixMode
from common.NMEA.nmea_instance import NMEAInstance
from common.NMEA.nmea_data_types import ZDA, GLL, GSA, GSV, RMC, VTG, GGA


def GGA_parser(instance: NMEAInstance):
    data = instance.nmea_str.split('*')[0].split(',')
    gga_data: GGA = GGA()

    if not instance.validate():
        print("Invalid checksum for GGA sentence!")
        return


    gga_data.utc = time(
        hour=int(data[1][0:2]),
        minute=int(data[1][2:4]),
        second=int(data[1][4:6]),
        microsecond=int(data[1].split('.')[1])
    )

    gga_data.coordinates = Coordinates(
        Latitude(int(data[2][0:2]), float(data[2][2:]) , Hemisphere(data[3])),
        Longitude(int(data[4][0:3]), float(data[4][3:]), Hemisphere(data[5]))
    )

    gga_data.fix_quality = FixQuality(int(data[6]))
    gga_data.num_satellites = int(data[7])
    gga_data.hdop = float(data[8]) if data[8] else None
    gga_data.altitude = Altitude(float(data[9]), DistanceMeasureUnit(data[10]))
    gga_data.geoid_height = Altitude(float(data[11]), DistanceMeasureUnit(data[12]))
    gga_data.time_since_last_dgps = float(data[13]) if data[13] else None
    gga_data.dgps_reference_station_id = data[14] if data[14] else None
    instance._data = gga_data



def GLL_parser(instance: NMEAInstance):
    data = instance.nmea_str.split('*')[0].split(',')
    gll_data: GLL = GLL()

    if not instance.validate():
        print("Invalid checksum for GLL sentence!")
        return


    gll_data.coordinates = Coordinates(
        Latitude(int(data[1][0:2]), float(data[1][2:]) , Hemisphere(data[2])),
        Longitude(int(data[3][0:3]), float(data[3][3:]), Hemisphere(data[4]))
    )

    gll_data.utc = time(
        hour=int(data[5][0:2]),
        minute=int(data[5][2:4]),
        second=int(data[5][4:6]),
        microsecond=int(data[5].split('.')[1])
    )
    gll_data.status = StatusIndicator(data[6])
    gll_data.mode = ModeIndicator(data[7])
    instance._data = gll_data



def GSA_parser(instance: NMEAInstance):
    data = instance.nmea_str.split('*')[0].split(',')
    gsa_data: GSA = GSA()

    if not instance.validate():
        print("Invalid checksum for GSA sentence!")
        return


    gsa_data.mode = ModeIndicator(data[1])
    gsa_data.fix_mode = FixMode(int(data[2]))
    gsa_data.pdop = float(data[-3]) if data[-3] else None
    gsa_data.hdop = float(data[-2]) if data[-2] else None
    gsa_data.vdop = float(data[-1]) if data[-1] else None
    gsa_data.satellite_ids = [int(sat_id) for sat_id in data[3:15] if sat_id]
    instance._data = gsa_data


def GSV_parser(instance: NMEAInstance):
    data = instance.nmea_str.split('*')[0].split(',')
    gsv_data: GSV = GSV()

    if not instance.validate():
        print("Invalid checksum for GSV sentence!")
        return


    sat_info_num = (len(data) - 4) // 4
    gsv_data.num_msgs = int(data[1])
    gsv_data.msg_num = int(data[2])
    gsv_data.num_satellites = int(data[3])
    gsv_data.satellite_info = [SatelliteInfo(
        satellite_id=int(data[i]),
        elevation=int(data[i + 1]) if data[i + 1] else None,
        azimuth=int(data[i + 2]) if data[i + 2] else None,
        snr=int(data[i + 3]) if data[i + 3] else None,
    ) for i in range(4, 4 + 4 * sat_info_num, 4) if data[i]]
    instance._data = gsv_data



def RMC_parser(instance: NMEAInstance):
    data = instance.nmea_str.split('*')[0].split(',')
    rmc_data: RMC = RMC()

    if not instance.validate():
        print("Invalid checksum for RMC sentence!")
        return


    rmc_data.utc = time(
        hour=int(data[1][0:2]),
        minute=int(data[1][2:4]),
        second=int(data[1][4:6]),
        microsecond=int(data[1].split('.')[1])
    )

    rmc_data.status = StatusIndicator(data[2])
    rmc_data.coordinates = Coordinates(
        Latitude(int(data[3][0:2]), float(data[3][2:]) , Hemisphere(data[4])),
        Longitude(int(data[5][0:3]), float(data[5][3:]), Hemisphere(data[6]))
    )
    rmc_data.speed_over_ground_knots = float(data[7]) if data[7] else None
    rmc_data.true_course_over_ground_degrees = float(data[8]) if data[8] else None
    date_: date = date(
        year=int(data[9][4:6]) + 2000,
        month=int(data[9][2:4]),
        day=int(data[9][0:2])
    )
    rmc_data.date = date_
    rmc_data.magnetic_variation_degrees = float(data[10]) if data[10] else None
    rmc_data.magnetic_variation_direction = Hemisphere(data[11]) if data[11] else None
    rmc_data.mode = ModeIndicator(data[12]) if data[12] else None
    instance._data = rmc_data


def VTG_parser(instance: NMEAInstance):
    data = instance.nmea_str.split('*')[0].split(',')
    vtg_data: VTG = VTG()

    if not instance.validate():
        print("Invalid checksum for VTG sentence!")
        return

    vtg_data.true_course_over_ground_degrees = float(data[1]) if data[1] else None
    vtg_data.magnetic_course_over_ground_degrees = float(data[3]) if data[3] else None
    vtg_data.speed_over_ground_knots = float(data[5]) if data[5] else None
    vtg_data.speed_over_ground_kmh = float(data[7]) if data[7] else None
    vtg_data.mode = ModeIndicator(data[9]) if data[9] else None
    instance._data = vtg_data


def ZDA_parser(instance: NMEAInstance):
    data = instance.nmea_str.split('*')[0].split(',')
    zda_data: ZDA = ZDA()

    if not instance.validate():
        print("Invalid checksum for ZDA sentence!")
        return


    zda_data.utc = time(
        hour=int(data[1][0:2]),
        minute=int(data[1][2:4]),
        second=int(data[1][4:6]),
        microsecond=int(data[1].split('.')[1])
    )

    date_: date = date(
        year=int(data[4]),
        month=int(data[3]),
        day=int(data[2])
    )
    zda_data.date = date_
    zda_data.local_zone_hours = int(data[5]) if data[5] else None
    zda_data.local_zone_minutes = int(data[6]) if data[6] else None
    instance._data = zda_data
