import math
from dataclasses import dataclass
from math import radians, sqrt, sin, cos

from common.nmea_enum import DistanceMeasureUnit, Hemisphere, Ellipsoids
from constants.WGS_84 import a as a_wgs84, f as f_wgs84, b as b_wgs84
from constants.PZ_90 import a as a_pz90, f as f_pz90, b as b_pz90
from constants.GRS_80 import a as a_grs80, f as f_grs80, b as b_grs80


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



    def to_dd(self):
        value = self.degrees + self.minutes / 60
        return value if self.lat_dir == Hemisphere.NORTH else -value



    def to_dms(self):
        total_minutes = self.minutes
        seconds = (total_minutes - int(total_minutes)) * 60
        minutes = int(total_minutes)
        return self.degrees, minutes, seconds, self.lat_dir



@dataclass
class Longitude:
    degrees: int        = None
    minutes: float      = None
    lon_dir: Hemisphere = None

    @classmethod
    def from_dms(cls, degrees: int, minutes: float, seconds: float, lon_dir: Hemisphere):
        total_minutes = minutes + seconds / 60
        return cls(degrees, total_minutes, lon_dir)



    def to_dd(self):
        value = self.degrees + self.minutes / 60
        return value if self.lon_dir == Hemisphere.EAST else -value



    def to_dms(self):
        total_minutes = self.minutes
        seconds = (total_minutes - int(total_minutes)) * 60
        minutes = int(total_minutes)
        return self.degrees, minutes, seconds, self.lon_dir



@dataclass
class Coordinates:
    lat: Latitude   = None
    lon: Longitude  = None



@dataclass
class CartesianCoordinates:
    x: float = None
    y: float = None
    z: float = None

    def xyz_to_llh(self, ellipsoid: Ellipsoids = None):
        if ellipsoid is None:
            print("No ellipsoid provided for LLH to XYZ conversion! Defaulting to WGS 84.")
            ellipsoid = Ellipsoids.WGS_84


        ellipsoid_params = {
            Ellipsoids.WGS_84: (a_wgs84, f_wgs84, b_wgs84),
            Ellipsoids.PZ_90: (a_pz90, f_pz90, b_pz90),
            Ellipsoids.GRS_80: (a_grs80, f_grs80, b_grs80),
        }

        a, f, b = ellipsoid_params[ellipsoid]

        lat: float = 0
        lon: float = 0
        alt: float = 0

        # Auxiliary intermediate variables fo
        r = sqrt(pow(self.x, 2) + pow(self.y, 2))
        e_2 = 1 - pow(b, 2) / pow(a, 2)
        e_p_2 = pow(a, 2) / pow(b, 2) - 1

        F = 54 * pow(b, 2) * pow(self.z, 2)
        G = pow(r, 2) + (1 - e_2) * pow(self.z, 2) - e_2 * (pow(a, 2) - pow(b, 2))
        c = (pow(e_2, 2) * F * pow(r, 2) ) / pow(G, 3)
        s = pow(1 + c + sqrt(pow(c, 2) + 2 * c), 1/3)
        P = F / (3 * pow(s + 1/s + 1, 2) * pow(G, 2))
        Q = sqrt(1 + 2 * pow(e_2, 2) * P)
        r_0 = -(P * e_2 * r) / (1 + Q) + sqrt((pow(a, 2)/2) * (1 + 1/Q) - (P * (1 - e_2) * pow(self.z, 2)/(Q * (1 + Q))) - P * pow(r, 2)/2)
        U = sqrt(pow(r - e_2 * r_0, 2) + pow(self.z, 2))
        V = sqrt(pow(r - e_2 * r_0, 2) + (1 - e_2) * pow(self.z, 2))
        Z_0 = (pow(b, 2) * self.z) / (a * V)

        # Vermeille's method for XYZ to LLH conversion
        if self.y >= 0:
            lon = math.pi / 2 - 2 * math.atan(self.x / (r + self.y))
        else:
            lon = - math.pi / 2 - 2 * math.atan(self.x / (r - self.y))


        lat = math.atan((self.z + e_p_2 * Z_0) / r)
        alt = U * (1 - pow(b, 2) / (a * V))

        return lat, lon, alt



@dataclass
class LLH:
    coordinates: Coordinates = None
    altitude: Altitude = None

    # Method to convert LLH to XYZ coordinates using the specified ellipsoid parameters
    def llh_to_xyz(self, ellipsoid: Ellipsoids = None) -> CartesianCoordinates:
        if ellipsoid is None:
            print("No ellipsoid provided for LLH to XYZ conversion! Defaulting to WGS 84.")
            ellipsoid = Ellipsoids.WGS_84


        ellipsoid_params = {
            Ellipsoids.WGS_84: (a_wgs84, f_wgs84),
            Ellipsoids.PZ_90: (a_pz90, f_pz90),
            Ellipsoids.GRS_80: (a_grs80, f_grs80),
        }

        a, f = ellipsoid_params[ellipsoid]

        rad_lat: float = radians(self.coordinates.lat.to_dd())
        rad_lon: float = radians(self.coordinates.lon.to_dd())
        rn = a / (sqrt(1 - f * (2 - f) * pow(sin(rad_lat), 2)))         # Radius of curvature in the prime vertical
        x = (rn + self.altitude.value) * cos(rad_lat) * cos(rad_lon)
        y = (rn + self.altitude.value) * cos(rad_lat) * sin(rad_lon)
        z = (pow((1 - f), 2) * rn + self.altitude.value) * sin(rad_lat)
        return CartesianCoordinates(x, y, z)



@dataclass
class SatelliteInfo:
    satellite_id: int = None
    elevation: int = None
    azimuth: int = None
    snr: int = None