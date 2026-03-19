from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Callable, Optional

from common.data_components import Coordinates, Latitude, Longitude, SatelliteInfo
from common.NMEA.nmea_enum import NMEAType, StatusIndicator, ModeIndicator
from common.NMEA.nmea_instance import NMEAInstance


class NMEAManager:
    nmea_instances: Dict[NMEAType, List[NMEAInstance]] = defaultdict(list)

    def get_instances_by_type(self, nmea_type: NMEAType, condition: Optional[Callable[[NMEAInstance], bool]] = None) \
            -> List[NMEAInstance]:
        if condition is None:
            return self.nmea_instances[nmea_type]

        return [item for item in self.nmea_instances[nmea_type] if condition(item)]



    def get_instances(self, condition: Optional[Callable[[NMEAInstance], bool]] = None) -> List[NMEAInstance]:
        if condition is None:
            return [item for sublist in self.nmea_instances.values() for item in sublist]

        return [item for sublist in self.nmea_instances.values() for item in sublist if condition(item)]



    def add_instance(self, instance: NMEAInstance):
        if instance.type is None:
            print("Cannot add instance with invalid type!")
            return

        self.nmea_instances[instance.type].append(instance)



    def get_recording_time(self):
        valid_zda: List[NMEAInstance] = self.get_instances_by_type(NMEAType.ZDA, lambda x: x.valid)
        if not valid_zda:
            print("No ZDA data, try other type (not implemented yet)!")
            return 100000000

        first_zda: NMEAInstance = self.nmea_instances[NMEAType.ZDA][0]
        last_zda: NMEAInstance = self.nmea_instances[NMEAType.ZDA][-1]
        first_datetime: datetime = datetime.combine(first_zda.data.date, first_zda.data.utc)
        last_datetime: datetime = datetime.combine(last_zda.data.date, last_zda.data.utc)
        return (last_datetime - first_datetime).total_seconds(), first_datetime, last_datetime



    # This method exists to fix message of rate for GSV messages
    def total_msgs(self, nmea_type: NMEAType) -> int:
        # Removing the repeated messages from GSV
        if nmea_type == NMEAType.GSV:
            instances = self.nmea_instances[nmea_type]
            l = len(instances)
            i = 0
            while i < len(instances):
                l -= instances[i].data.num_msgs - 1
                i += instances[i].data.num_msgs
            return l
        else:
            return len(self.nmea_instances[nmea_type])


    ### Processing ###
    # How do I do this????
    def lat_lon_box(self):
        cond: Callable[[NMEAInstance], bool] = lambda x: x.data.status == StatusIndicator.ACTIVE and x.valid == True
        coordinates: List[Coordinates] = [c.data.coordinates for c in self.get_instances_by_type(NMEAType.GLL, cond)]
        lats: List[Latitude] = [l.lat for l in coordinates]
        lons: List[Longitude] = [l.lon for l in coordinates]
        max_lat: Latitude = max(lats, key=lambda x: x.to_dd())
        min_lat: Latitude = min(lats, key=lambda x: x.to_dd())
        max_lon: Longitude = max(lons, key=lambda x: x.to_dd())
        min_lon: Longitude = min(lons, key=lambda x: x.to_dd())
        return max_lat, min_lat, max_lon, min_lon



    def max_min_altitude(self):
        cond: Callable[[NMEAInstance], bool] = lambda x: x.data.fix_quality.value not in [0, 6, 7, 8] and x.valid == True
        altitudes: List[NMEAInstance] = self.get_instances_by_type(NMEAType.GGA, cond)
        max_altitude: NMEAInstance = max(altitudes, key=lambda x: x.data.altitude.value)
        min_altitude: NMEAInstance = min(altitudes, key=lambda x: x.data.altitude.value)
        return max_altitude, min_altitude



    def cumulative_elevation(self, loss: bool = False) -> float:
        cond: Callable[[NMEAInstance], bool] = lambda x: x.data.fix_quality.value not in [0, 6, 7,8] and x.valid == True
        altitudes: List[float] = [a.data.altitude.value for a in self.get_instances_by_type(NMEAType.GGA, cond)]

        gain: float = 0
        for i in range(1, len(altitudes)):
            if loss and altitudes[i] < altitudes[i-1]:
                gain -= altitudes[i-1] - altitudes[i]
            elif not loss and altitudes[i] > altitudes[i-1]:
                gain += altitudes[i] - altitudes[i-1]
        return gain



    def get_max_speed_over_groud(self) -> NMEAInstance:
        cond: Callable[[NMEAInstance], bool] = lambda x: x.valid == True and (x.data.mode in [ModeIndicator.AUTONOMOUS, ModeIndicator.DIFFERENTIAL])
        speeds: List[NMEAInstance] = self.get_instances_by_type(NMEAType.VTG, cond)
        return max(speeds, key=lambda x: x.data.speed_over_ground_kmh)



    def get_max_number_of_sat_in_view(self) -> NMEAInstance:
        cond: Callable[[NMEAInstance], bool] = lambda x: x.valid == True
        num_sats: List[NMEAInstance] = self.get_instances_by_type(NMEAType.GSV, cond)
        return max(num_sats, key=lambda x: x.data.num_satellites)



    def get_max_elevation_angle_sat(self) -> SatelliteInfo:
        cond: Callable[[NMEAInstance], bool] = lambda x: x.valid == True
        satellite_infos: List[SatelliteInfo] = [sat_info for instance in self.get_instances_by_type(NMEAType.GSV, cond) for sat_info in instance.data.satellite_info]
        return max(satellite_infos, key=lambda x: x.elevation is not None and x.elevation)

    ### End Processing ###

    def print_status(self):
        for instance_type in self.nmea_instances.keys():
            total_instances = len(self.nmea_instances[instance_type])
            valid_instances = len(self.get_instances_by_type(instance_type, lambda x: x.valid))
            valid_percentage = valid_instances / total_instances
            rate = self.total_msgs(instance_type) / self.get_recording_time()[0]

            print(f"""
                {instance_type}:
                    - Number of instances: {total_instances}
                    - Valid %:  {valid_percentage:.2%}
                    - Rate (Hz): {rate:.3f}
            """)

        _, begin_date, last_date = self.get_recording_time()
        max_elevation_angle_sat: SatelliteInfo = self.get_max_elevation_angle_sat()
        max_num_sat_in_view: int = self.get_max_number_of_sat_in_view().data.num_satellites
        max_speed_over_ground: float = self.get_max_speed_over_groud().data.speed_over_ground_kmh
        cumulative_elevation_gain = self.cumulative_elevation(False)
        cumulative_elevation_loss = self.cumulative_elevation()
        max_altitude, min_altitude = self.max_min_altitude()
        min_lat, max_lat, min_lon, max_lon = self.lat_lon_box()
        print(f"""
            Recording Start: {begin_date}
            Recording End: {last_date}
            Upper Left Corner (NW): Lat={min_lat.degrees}°{min_lat.minutes}"{min_lat.lat_dir.value} Lon={max_lon.degrees}°{max_lon.minutes}"{max_lon.lon_dir.value}
            Lower Right Corner (SE): Lat={max_lat.degrees}°{max_lat.minutes}"{max_lat.lat_dir.value} Lon={min_lon.degrees}°{min_lon.minutes}"{min_lon.lon_dir.value}
            Max Altitude: {max_altitude.data.altitude.value} {max_altitude.data.altitude.unit.value} at {max_altitude.data.coordinates.lat.degrees}°{max_altitude.data.coordinates.lat.minutes}"{max_altitude.data.coordinates.lat.lat_dir.value} {max_altitude.data.coordinates.lon.degrees}°{max_altitude.data.coordinates.lon.minutes}"{max_altitude.data.coordinates.lon.lon_dir.value}
            Time of Max Altitude: {max_altitude.data.utc}
            Min Altitude: {min_altitude.data.altitude.value} {min_altitude.data.altitude.unit.value} at {min_altitude.data.coordinates.lat.degrees}°{min_altitude.data.coordinates.lat.minutes}"{min_altitude.data.coordinates.lat.lat_dir.value} {min_altitude.data.coordinates.lon.degrees}°{min_altitude.data.coordinates.lon.minutes}"{min_altitude.data.coordinates.lon.lon_dir.value}
            Time of Min Altitude: {min_altitude.data.utc}
            Cumulative Elevation Gain: {cumulative_elevation_gain:.2f} {max_altitude.data.altitude.unit.value}
            Cumulative Elevation Loss: {cumulative_elevation_loss:.2f} {max_altitude.data.altitude.unit.value}
            Max Speed Over Ground: {max_speed_over_ground:.2f} km/h
            Max Number of Satellites in View: {max_num_sat_in_view}
            Max Elevation Angle Satellite:
                - Satellite ID: {max_elevation_angle_sat.satellite_id}
                - Elevation: {max_elevation_angle_sat.elevation}°
                - Azimuth: {max_elevation_angle_sat.azimuth}°
                - SNR: {max_elevation_angle_sat.snr} dB
        """)
