from typing import List, Tuple

from common.Orbits.Ephemeris import Ephemeris


class EphemerisParser:
    eph_orbits: List[Tuple[int, Ephemeris]] = []

    def __init__(self, file):
        self.file = file

    def parse(self):
        with open(self.file, "r", encoding="utf-8") as f:
            for line in f:
                fields = line.split()
                if not fields:
                    continue

                sv = int(fields[0])  # Field (1)

                eph = Ephemeris(
                    SVN=sv,
                    sqrt_a=float(fields[33]),  # Field (34)
                    toe=float(fields[6]),  # Field (7)
                    WN=int(fields[3]),  # Field (4)
                    M0=float(fields[39]),  # Field (40)
                    e=float(fields[42]),  # Field (43)
                    i0=float(fields[48]),  # Field (49)
                    lon0=float(fields[54]),  # Field (55) - Omega0
                    omega=float(fields[45]),  # Field (46) - Argument of Perigee
                    dn=float(fields[36]),  # Field (37) - Delta n
                    dotlon=float(fields[57]),  # Field (58) - Omega Dot
                    IDOT=float(fields[51]),  # Field (52)
                    cuc=float(fields[60]),  # Field (61)
                    cus=float(fields[63]),  # Field (64)
                    crc=float(fields[66]),  # Field (67)
                    crs=float(fields[69]),  # Field (70)
                    cic=float(fields[72]),  # Field (73)
                    cis=float(fields[75]),  # Field (76)
                    IODE=int(fields[2])  # Field (3)
                )

                self.eph_orbits.append((sv, eph))

        return self.eph_orbits
