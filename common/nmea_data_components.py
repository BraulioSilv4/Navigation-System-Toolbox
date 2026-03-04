from __future__ import annotations

import math
import numpy as np
from dataclasses import dataclass
from math import radians, sqrt, sin, cos
from typing import Optional

from common.nmea_enum import DistanceMeasureUnit, Hemisphere, Ellipsoids
from constants.GRS_80 import a as a_grs80, f as f_grs80, b as b_grs80, e as e_grs80
from constants.PZ_90 import a as a_pz90, f as f_pz90, b as b_pz90, e as e_pz90
from constants.WGS_84 import a as a_wgs84, f as f_wgs84, b as b_wgs84, e as e_wgs84


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



# Improve this class for duplicated code with Longitude
@dataclass
class Latitude:
    degrees: int        = None
    minutes: float      = None
    lat_dir: Hemisphere = None


    @classmethod
    def from_dms(cls, degrees: int, minutes: float, seconds: float, lat_dir: Hemisphere):
        total_minutes = minutes + seconds / 60
        return cls(degrees, total_minutes, lat_dir)


    @classmethod
    def from_dd(cls, dd: float):
        degrees = int(abs(dd))
        minutes = (abs(dd) - degrees) * 60
        lat_dir = Hemisphere.NORTH if dd >= 0 else Hemisphere.SOUTH
        return cls(degrees, minutes, lat_dir)


    def to_dd(self):
        value = self.degrees + self.minutes / 60
        return value if self.lat_dir == Hemisphere.NORTH else -value


    def to_dms(self):
        total_minutes = self.minutes
        seconds = (total_minutes - int(total_minutes)) * 60
        minutes = int(total_minutes)
        return self.degrees, minutes, seconds, self.lat_dir



# Format DDDMM.mmm for longitude, DDMM.mmm for latitude
@dataclass
class Longitude:
    degrees: int        = None
    minutes: float      = None
    lon_dir: Hemisphere = None


    @classmethod
    def from_dms(cls, degrees: int, minutes: float, seconds: float, lon_dir: Hemisphere):
        total_minutes = minutes + seconds / 60
        return cls(degrees, total_minutes, lon_dir)


    @classmethod
    def from_dd(cls, dd: float):
        degrees = int(abs(dd))
        minutes = (abs(dd) - degrees) * 60
        lon_dir = Hemisphere.EAST if dd >= 0 else Hemisphere.WEST
        return cls(degrees, minutes, lon_dir)


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
class ECEF:
    x: float = None
    y: float = None
    z: float = None


    def ecef_to_llh(self, ellipsoid: Ellipsoids = None) -> LLH:
        if ellipsoid is None:
            print("No ellipsoid provided for LLH to XYZ conversion! Defaulting to WGS 84.")
            ellipsoid = Ellipsoids.WGS_84


        ellipsoid_params = {
            Ellipsoids.WGS_84: (a_wgs84, f_wgs84, b_wgs84),
            Ellipsoids.PZ_90: (a_pz90, f_pz90, b_pz90),
            Ellipsoids.GRS_80: (a_grs80, f_grs80, b_grs80),
        }

        a, f, b = ellipsoid_params[ellipsoid]

        # Auxiliary intermediate variables fo
        r = sqrt(pow(self.x, 2) + pow(self.y, 2))
        e_2 = 1 - (pow(b, 2) / pow(a, 2))
        e_p_2 = (pow(a, 2) / pow(b, 2)) - 1

        F = 54 * pow(b, 2) * pow(self.z, 2)
        G = pow(r, 2) + (1 - e_2) * pow(self.z, 2) - e_2 * (pow(a, 2) - pow(b, 2))
        c = (pow(e_2, 2) * F * pow(r, 2) ) / pow(G, 3)
        s = pow(1 + c + sqrt(pow(c, 2) + 2 * c), 1/3)
        P = F / (3 * pow(s + 1/s + 1, 2) * pow(G, 2))
        Q = sqrt(1 + 2 * pow(e_2, 2) * P)
        r_0 = -(P * e_2 * r) / (1 + Q) + sqrt((pow(a, 2)/2) * (1 + 1/Q) - (P * (1 - e_2) * pow(self.z, 2)
                                                                           / (Q * (1 + Q))) - P * pow(r, 2)/2)
        U = sqrt(pow(r - e_2 * r_0, 2) + pow(self.z, 2))
        V = sqrt(pow(r - e_2 * r_0, 2) + (1 - e_2) * pow(self.z, 2))
        Z_0 = (pow(b, 2) * self.z) / (a * V)

        # Vermeille's method for XYZ to LLH conversion
        if self.y >= 0:
            lon = math.degrees((math.pi / 2) - 2 * math.atan(self.x / (r + self.y)))
        else:
            lon = math.degrees((-math.pi / 2) + 2 * math.atan(self.x / (r - self.y)))


        # Heikkinen's method for XYZ to LLH conversion
        lat = math.degrees(math.atan((self.z + e_p_2 * Z_0) / r))
        alt = U * (1 - pow(b, 2) / (a * V))

        return LLH(
            Coordinates(
                Latitude.from_dd(lat),
                Longitude.from_dd(lon)
            ),
            Altitude(alt, DistanceMeasureUnit.METERS)
        )


    def ecef_to_enu(self, target: ECEF) -> ENU:
        geodetic: LLH = self.ecef_to_llh()
        rad_lat = radians(geodetic.coordinates.lat.to_dd())
        rad_lon = radians(geodetic.coordinates.lon.to_dd())

        dx = target.x - self.x
        dy = target.y - self.y
        dz = target.z - self.z

        lamb = rad_lon + math.pi / 2
        alpha = math.pi / 2 - rad_lat
        rot_z = np.array([
            [cos(lamb), sin(lamb), 0],
            [-sin(lamb), cos(lamb), 0],
            [0, 0, 1]
        ])

        rot_x = np.array([
            [1, 0, 0],
            [0, cos(alpha), sin(alpha)],
            [0, -sin(alpha), cos(alpha)]
        ])

        enu = rot_x @ (rot_z @ np.array([dx, dy, dz]))
        return ENU(enu[0], enu[1], enu[2])



@dataclass
class LLH:
    coordinates: Coordinates = None
    altitude: Altitude = None


    # Method to convert LLH to XYZ coordinates using the specified ellipsoid parameters
    def llh_to_ecef(self, ellipsoid: Ellipsoids = None) -> ECEF:
        if ellipsoid is None:
            print("No ellipsoid provided for LLH to ECEF conversion! Defaulting to WGS 84.")
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
        return ECEF(x, y, z)


    # IDK if I should call the ellipsoid datum or not. Ill just call it datum for now.
    def molodensky_transform(self, source: Ellipsoids = Ellipsoids.WGS_84, target: Datum = None) -> Optional[LLH]:
        if source or target is None:
            print("Molodensky transformation requires both source and target datums.")
            return None


        ellipsoid_params = {
            Ellipsoids.WGS_84: (a_wgs84, b_wgs84, e_wgs84),
            Ellipsoids.PZ_90: (a_pz90, b_pz90, e_pz90),
            Ellipsoids.GRS_80: (a_grs80, b_grs80, e_grs80),
        }

        a, b, e = ellipsoid_params[source]

        rad_lat = radians(self.coordinates.lat.to_dd())
        rad_lon = radians(self.coordinates.lon.to_dd())

        R_n = a / sqrt(1 - pow(e, 2) * pow(sin(rad_lat), 2))
        R_m = a * (1 - pow(e, 2)) / math.sqrt(pow(1 - pow(e, 2) * pow(sin(rad_lat), 2), 3))

        d_lat_rad = (((-target.dx * math.sin(rad_lat) * math.cos(rad_lon)) - (target.dy * math.sin(rad_lat) * math.sin(rad_lon)) + (target.dz * math.cos(rad_lat)) + (
                    target.da * ((R_n * pow(e, 2)) / a) + target.df * (R_m * (a / b) + R_n * (b / a))) * math.sin(rad_lat) * math.cos(rad_lat)) /
                     (R_m + self.altitude.value))
        d_lon_rad = ((-target.dx * math.sin(rad_lon)) + (target.dy * math.cos(rad_lon))) / ((R_n + self.altitude.value) * math.cos(rad_lat))
        d_h = (target.dx * math.cos(rad_lat) * math.cos(rad_lon)) + (target.dy * math.cos(rad_lat) * math.sin(rad_lon)) + (target.dz * math.sin(rad_lat)) - (target.da * (a / R_n)) + (target.df * ((b / a) * R_n * pow(sin(rad_lat), 2)))

        new_lat = self.coordinates.lat.to_dd() + math.degrees(d_lat_rad)
        new_lon = self.coordinates.lon.to_dd() + math.degrees(d_lon_rad)
        new_alt = self.altitude.value + d_h

        return LLH(
            Coordinates(
                Latitude.from_dd(new_lat),
                Longitude.from_dd(new_lon)
            ),
            Altitude(new_alt, DistanceMeasureUnit.METERS)
        )



@dataclass
class ENU:
    e: float = None
    n: float = None
    u: float = None


    def azimuth(self) -> float:
        return math.degrees(math.atan2(self.e, self.n))


    def elevation(self) -> float:
        horizontal_dist = math.sqrt(pow(self.e, 2) + pow(self.n, 2))
        return math.degrees(math.atan2(self.u, horizontal_dist))



@dataclass
class Datum:
    da: float = None
    df: float = None
    dx: float = None
    dy: float = None
    dz: float = None



@dataclass
class SatelliteInfo:
    satellite_id: int = None
    elevation: int = None
    azimuth: int = None
    snr: int = None