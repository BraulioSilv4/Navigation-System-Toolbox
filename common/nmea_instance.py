from dataclasses import dataclass
from typing import Union, Optional

from common.nmea_data_components import Checksum
from common.nmea_data_types import GGA, GLL, GSA, GSV, RMC, VTG, ZDA
from common.nmea_enum import Constellation, NMEAType


@dataclass
class NMEAInstance:
    def __init__(self, data):
        self.nmea_str = data
        self._data: Optional[Union[GGA, GLL, GSA, GSV, RMC, VTG, ZDA]] = None
        self._valid: Optional[bool] = None
        try:
            self.constellation = Constellation[data[1:3]]
            self.type = NMEAType[data[3:6]]
        except KeyError:
            print(f"Invalid constellation or NMEA type in sentence: {data}")
            self.constellation = None
            self.type = None


    constellation: Optional[Constellation] = None
    type: Optional[NMEAType] = None
    nmea_str: str = None


    @property
    def valid(self):
        if self._valid is None:
            self._valid = self.validate()
        return self._valid


    @property
    def data(self):
        if self._data is None:
            self.parse()
        return self._data


    @data.setter
    def data(self, value):
        self._data = value


    def parse(self):
        if self.nmea_str is None:
            print("No valid data to construct instance!")
            return

        if self.type == NMEAType.GGA:
            from .nmea_parsers import GGA_parser
            GGA_parser(self)
        elif self.type == NMEAType.GLL:
            from .nmea_parsers import GLL_parser
            GLL_parser(self)
        elif self.type == NMEAType.RMC:
            from .nmea_parsers import RMC_parser
            RMC_parser(self)
        elif self.type == NMEAType.GSA:
            from .nmea_parsers import GSA_parser
            GSA_parser(self)
        elif self.type == NMEAType.GSV:
            from .nmea_parsers import GSV_parser
            GSV_parser(self)
        elif self.type == NMEAType.VTG:
            from .nmea_parsers import VTG_parser
            VTG_parser(self)
        elif self.type == NMEAType.ZDA:
            from .nmea_parsers import ZDA_parser
            ZDA_parser(self)
        else:
            print("No parser implemented for this NMEA type!")

        return

    def validate(self):
        checksum_str = self.nmea_str.split('*')[1]
        checksum: Checksum = Checksum(int(checksum_str, 16))
        valid = checksum.validate_checksum(self.nmea_str)
        self._valid = valid
        return valid