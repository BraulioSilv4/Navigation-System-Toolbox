import math
from dataclasses import dataclass

from common.data_components import ECEF

gravitational_constant = 3.986005e14 # m^3/s^2
earth_rotation_rate = 7.2921151467e-5 # rad/s
c = 299792458.0 # Speed of light in m/s


def calc_dt(wna: int, towa: float, wnb: int, towb: float) -> float:
    dt = (wna - wnb) * 604800 + (towa - towb)
    if dt > 302400:
        dt -= 604800
    elif dt < -302400:
        dt += 604800
    return dt


@dataclass
class Ephemeris:
    SVN: int = 0
    sqrt_a: float = 0.0
    toe: float = 0.0
    WN: int = 0
    M0: float = 0.0
    e: float = 0.0
    i0: float = 0.0
    lon0: float = 0.0
    omega: float = 0.0
    dn: float = 0.0  # Delta n
    dotlon: float = 0.0  # Omega dot
    cuc: float = 0.0
    cus: float = 0.0
    crc: float = 0.0
    crs: float = 0.0
    cic: float = 0.0
    cis: float = 0.0
    IDOT: float = 0.0
    IODE: int = 0

    def TOW_at_perigee_passage(self):
        a = pow(self.sqrt_a, 2)
        n0 = math.sqrt(gravitational_constant / pow(a, 3))
        n = n0 + self.dn
        return self.toe - (self.M0 / n)


    def TOW_of_first_perigee_passage(self):
        a = pow(self.sqrt_a, 2)
        n0 = math.sqrt(gravitational_constant / pow(a, 3))
        n = n0 + self.dn
        period = 2 * math.pi / n
        t = self.TOW_at_perigee_passage()
        while t > 0:
            t -= period

        return t + period


    # t is the time at which we want to calculate the satellite position, in seconds since the beginning of the week.
    def calculate_position(self, t: float) -> ECEF:
        # Orbit semi-major axis
        a = pow(self.sqrt_a, 2)

        # Corrected satellite mean angular velocity
        n0 = math.sqrt(gravitational_constant / pow(a, 3))
        n = n0 + self.dn

        # Time difference
        dt = t - self.toe
        if dt > 302400:
            dt -= 604800
        elif dt < -302400:
            dt += 604800

        # Mean anomaly
        M = self.M0 + n * dt

        # Eccentric anomaly
        E = self._solve_kepler(M)

        # True anomaly
        y_ta = math.sqrt(1 - pow(self.e, 2)) * math.sin(E)
        x_ta = math.cos(E) - self.e
        phi_o = math.atan2(y_ta, x_ta)

        # Argument of latitude
        phi = phi_o + self.omega

        # Corrected argument of latitude
        du = self.cuc * math.cos(2 * phi) + self.cus * math.sin(2 * phi)
        u = phi + du

        # Corrected orbit radius
        ro = a * (1 - self.e * math.cos(E))
        dr = self.crc * math.cos(2 * phi) + self.crs * math.sin(2 * phi)
        r = ro + dr

        # Corrected angle of inclination
        di = self.cic * math.cos(2 * phi) + self.cis * math.sin(2 * phi)
        i = self.i0 + di + (self.IDOT * dt)

        # Corrected longitude of the ascending node
        omega_t = self.lon0 + (self.dotlon - earth_rotation_rate) * dt - (earth_rotation_rate * self.toe)

        # ECEF Transformation
        x_plane = r * math.cos(u)
        y_plane = r * math.sin(u)

        x = x_plane * math.cos(omega_t) - y_plane * math.cos(i) * math.sin(omega_t)
        y = x_plane * math.sin(omega_t) + y_plane * math.cos(i) * math.cos(omega_t)
        z = y_plane * math.sin(i)

        return ECEF(x, y, z)

    def sat_position_at_tx(self, r: ECEF, t_rx: float, debug: bool = False):
        niter = 0
        dp = 0.0
        d = float('inf')
        s = ECEF(0.0, 0.0, 0.0)

        while math.fabs(dp - d) > 0.0001:  # 1 mm precision
            niter += 1
            d = dp  # d = d'

            ttx = t_rx - (d / c)
            if debug:
                print(f"SVN{self.SVN} Time of transmission: TOW={ttx}")

            s = self.calculate_position(ttx)
            if debug:
                print(f"SVN{self.SVN} Satellite position @ttx before rotation: {s}")

            dlon = earth_rotation_rate * (d / c)

            cos_dw = math.cos(dlon)
            sin_dw = math.sin(dlon)

            x_rot = s.x * cos_dw + s.y * sin_dw
            y_rot = -s.x * sin_dw + s.y * cos_dw
            z_rot = s.z

            s = ECEF(x_rot, y_rot, z_rot)
            if debug:
                print(f"SVN{self.SVN} Satellite position @ttx after rotation: {s}")

            dp = math.sqrt((s.x - r.x) ** 2 + (s.y - r.y) ** 2 + (s.z - r.z) ** 2)

        return s, niter



    def _solve_kepler(self, M: float):
        E = M
        for _ in range(10):
            E = E - (E - M - self.e * math.sin(E)) / (1 - self.e * math.cos(E))
        return E