import math
from dataclasses import dataclass

gravitational_constant = 3.986005e14 # m^3/s^2
earth_rotation_rate = 7.2921151467e-5 # rad/s

@dataclass
class KeplerianOrbit:
    a: float = 0.0 # semi-major axis in meters
    e: float = 0.0 # eccentricity
    tp: float = 0.0 # time of perigee passage in seconds
    i: float = 0.0 # inclination of the orbital plane in radians
    omega: float = 0.0 # argument of perigee in radians
    raan: float = 0.0 # right ascension of the ascending node in radians


    def argument_of_latitude(self, true_anomaly: float):
        # Starting position of the satellite from the equator.
        return self.omega + true_anomaly


    def radius_true_anomaly(self, E: float):
        y = self.a * math.sqrt(1 - pow(self.e, 2)) * math.sin(E)
        x = self.a * (math.cos(E) - self.e)
        radius = self.a * (1 - self.e * math.cos(E))
        true_anomaly = math.atan2(y, x)
        return radius, true_anomaly


    def eccentric_anomaly_default(self, M: float):
        niter = 0
        E = M
        Ep = float('inf')
        while math.fabs(E - Ep) > 1e-12: # epsilon
            niter += 1
            Ep = E
            E = M + self.e * math.sin(E)

        return E, niter


    def eccentric_anomaly_raphson(self, M: float):
        niter = 0
        E = M
        Ep = float('inf')
        while math.fabs(E - Ep) > 1e-12: # epsilon
            niter += 1
            Ep = E
            E = E - (E - M - self.e * math.sin(E)) / (1 - self.e * math.cos(E))

        return E, niter


    def mean_anomaly(self, t: float) -> float:
        # M = 0 at time of perigee passage, M = 180 halfway through the orbit, M = 360 at the end of the orbit.
        n = self.satellite_mean_motion()
        M = n * (t - self.tp)
        return M


    def satellite_mean_motion(self):
        # Velocity a satellite would have in a perfectly circular orbit.
        # n = 2pi/T
        return math.sqrt(gravitational_constant / pow(self.a, 3))


    def orbital_period(self):
        # T = 2pi / satellite_mean_motion
        return 2 * math.pi * math.sqrt(pow(self.a, 3) / gravitational_constant)


    def longitude_of_ascending_node(self, t: float):
        return self.raan - earth_rotation_rate * (t - self.tp)
