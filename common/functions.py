import math
from typing import Union

from common.data_components import LLH, ECEF
from common.NMEA.nmea_enum import Ellipsoids


def distance_between(this: Union[LLH, ECEF], target: Union[LLH, ECEF], ellipsoid: Ellipsoids) -> float:
    src: ECEF
    dst: ECEF

    if isinstance(this, LLH):
        src = this.llh_to_ecef(source=ellipsoid)
    else:
        src = this

    if isinstance(target, LLH):
        dst = target.llh_to_ecef(source=ellipsoid)
    else:
        dst = target

    return math.sqrt(pow(dst.x - src.x, 2) + pow(dst.y - src.y, 2) + pow(dst.z - src.z, 2))


