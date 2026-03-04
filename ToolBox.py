from typing import List, Callable, Tuple

from common.nmea_data_components import LLH
from common.nmea_data_manager import NMEAManager
from common.nmea_enum import NMEAType, Ellipsoids
from common.nmea_instance import NMEAInstance

path = r"data/ISTShuttle.nmea"

manager: NMEAManager = NMEAManager()

with open(path, "r", encoding="utf-8") as f:
    for line in f:
        instance = NMEAInstance(line)
        manager.add_instance(instance)


    # manager.print_status()

cond: Callable[[NMEAInstance], bool] = lambda x: x.data.fix_quality.value not in [0, 6, 7, 8] and x.valid == True
coordinates: List[LLH] = [LLH(c.data.coordinates, c.data.altitude) for c in manager.get_instances_by_type(NMEAType.GGA, cond)]
xyz_coords: List[Tuple[float, float, float]] = [c.llh_to_ecef(Ellipsoids.WGS_84) for c in coordinates]
