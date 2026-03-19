from common.NMEA.nmea_data_manager import NMEAManager
from common.NMEA.nmea_instance import NMEAInstance

path = r"../data/ISTShuttle.nmea"

manager: NMEAManager = NMEAManager()

with open(path, "r", encoding="utf-8") as f:
    for line in f:
        instance = NMEAInstance(line)
        manager.add_instance(instance)

manager.print_status()