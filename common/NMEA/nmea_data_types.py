from dataclasses import dataclass
from datetime import time, date
from typing import List

from common.data_components import Coordinates, Altitude, SatelliteInfo
from common.NMEA.nmea_enum import FixQuality, StatusIndicator, ModeIndicator, FixMode, Hemisphere


@dataclass
class GGA:
    utc: time = None
    coordinates: Coordinates = None
    fix_quality: FixQuality = None
    num_satellites: int = None
    hdop: float = None
    altitude: Altitude = None
    geoid_height: Altitude = None
    time_since_last_dgps: float = None
    dgps_reference_station_id: str = None



@dataclass
class GLL:
    utc: time = None
    coordinates: Coordinates = None
    status: StatusIndicator = None
    mode: ModeIndicator = None



@dataclass
class GSA:
    mode: ModeIndicator = None
    fix_mode: FixMode = None
    satellite_ids: list[int] = None
    pdop: float = None
    hdop: float = None
    vdop: float = None



@dataclass
class GSV:
    num_msgs: int = None
    msg_num: int = None
    num_satellites: int = None
    satellite_info: List[SatelliteInfo] = None


@dataclass
class RMC:
    utc: time = None
    status: StatusIndicator = None
    coordinates: Coordinates = None
    speed_over_ground_knots: float = None
    true_course_over_ground_degrees: float = None
    date: date = None
    magnetic_variation_degrees: float = None
    magnetic_variation_direction: Hemisphere = None
    mode: ModeIndicator = None


@dataclass
class VTG:
    true_course_over_ground_degrees: float = None
    magnetic_course_over_ground_degrees: float = None
    speed_over_ground_knots: float = None
    speed_over_ground_kmh: float = None
    mode: ModeIndicator = None


@dataclass
class ZDA:
    utc: time = None
    date: date = None
    local_zone_hours: int = None
    local_zone_minutes: int = None