from dataclasses import dataclass

@dataclass
class Almanac:
    WNa: int = 0 # Almanac reference week number.
    toa: float = 0.0 # Almanac reference time.
    M0: float = 0.0 #  Mean anomaly at the almanac reference time.
    sqrt_a: float = 0.0 # Square root of the orbit semi-major axis.
    e: float = 0.0 # Eccentricity of the orbit.
    lon0: float = 0.0 # Longitude (measured East) of ascending node at weekly epoch(beginning of the week).
    epsi: float = 0.0 # Correction term to the orbit inclination angle, relatively toi0 = 0.30 sc (sc: semicírculos)
    omega: float = 0.0 # Argument of perigee. It represents the angle, measured in the orbital plane, between the ascending node and the perigee.
    dot_lon: float = 0.0 # Correction term to the right ascension of the ascending node.