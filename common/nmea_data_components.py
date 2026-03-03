from dataclasses import dataclass
from math import radians, sqrt, sin, cos

from common.nmea_enum import DistanceMeasureUnit, Hemisphere, Ellipsoids
from constants.WGS_84 import a as a_wgs84, f as f_wgs84
from constants.PZ_90 import a as a_pz90, f as f_pz90
from constants.GRS_80 import a as a_grs80, f as f_grs80


@dataclass
class Checksum:
    value: int | None = None

    def validate_checksum(self, sentence: str) -> bool:
        if self.value is None:
            print("No checksum value provided for validation!")
            return False

        checksum = 0
        for c in range(len(sentence)):
            if sentence[c] == '*':
                break

            if sentence[c] == '$':
                continue

            checksum ^= ord(sentence[c])

        return checksum == self.value



@dataclass
class Altitude:
    value: float = None
    unit: DistanceMeasureUnit = None



@dataclass
class Latitude:
    degrees: int        = None
    minutes: float      = None
    lat_dir: Hemisphere = None

    @classmethod
    def from_dms(cls, degrees: int, minutes: float, seconds: float, lat_dir: Hemisphere):
        total_minutes = minutes + seconds / 60
        return cls(degrees, total_minutes, lat_dir)


    def to_signed_lat(self):
        value = self.degrees + self.minutes / 60
        return value if self.lat_dir == Hemisphere.NORTH else -value



@dataclass
class Longitude:
    degrees: int        = None
    minutes: float      = None
    lon_dir: Hemisphere = None

    @classmethod
    def from_dms(cls, degrees: int, minutes: float, seconds: float, lon_dir: Hemisphere):
        total_minutes = minutes + seconds / 60
        return cls(degrees, total_minutes, lon_dir)


    def to_signed_lon(self):
        value = self.degrees + self.minutes / 60
        return value if self.lon_dir == Hemisphere.EAST else -value



@dataclass
class Coordinates:
    lat: Latitude   = None
    lon: Longitude  = None



@dataclass
class LLH:
    coordinates: Coordinates = None
    altitude: Altitude = None

    def llh_to_xyz(self, ellipsoid: Ellipsoids):
        ellipsoid_params = {
            Ellipsoids.WGS_84: (a_wgs84, f_wgs84),
            Ellipsoids.PZ_90: (a_pz90, f_pz90),
            Ellipsoids.GRS_80: (a_grs80, f_grs80),
        }

        a, f = ellipsoid_params[ellipsoid]

        rad_lat: float = radians(self.coordinates.lat.to_signed_lat())
        rad_lon: float = radians(self.coordinates.lon.to_signed_lon())
        rn = a / (sqrt(1 - f * (2 - f) * pow(sin(rad_lat), 2)))
        x = (rn + self.altitude.value) * cos(rad_lat) * cos(rad_lon)
        y = (rn + self.altitude.value) * cos(rad_lat) * sin(rad_lon)
        z = (pow((1 - f), 2) * rn + self.altitude.value) * sin(rad_lat)
        return x,y,z

    # def xyz_to_llh(self):



@dataclass
class SatelliteInfo:
    satellite_id: int = None
    elevation: int = None
    azimuth: int = None
    snr: int = None