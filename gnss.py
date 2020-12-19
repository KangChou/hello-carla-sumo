#!/usr/bin/env python

#
# Copyright (c) 2018-2019 Intel Corporation
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.
#
"""
Classes to handle Carla gnsss
"""

from sensor_msgs.msg import NavSatFix

from carla_ros_bridge.sensor import Sensor


class Gnss(Sensor):

    """
    Actor implementation details for gnss sensor
    """

    def __init__(self, carla_actor, parent, communication, synchronous_mode):
        """
        Constructor
        :param carla_actor: carla actor object
        :type carla_actor: carla.Actor
        :param parent: the parent of this
        :type parent: carla_ros_bridge.Parent
        :param communication: communication-handle
        :type communication: carla_ros_bridge.communication
        :param synchronous_mode: use in synchronous mode?
        :type synchronous_mode: bool
        """
        super(Gnss, self).__init__(carla_actor=carla_actor,
                                   parent=parent,
                                   communication=communication,
                                   synchronous_mode=synchronous_mode,
                                   prefix="gnss/" + carla_actor.attributes.get('role_name'))

    # pylint: disable=arguments-differ
    def sensor_data_updated(self, carla_gnss_event):
        """
        Function to transform a received gnss event into a ROS NavSatFix message
        :param carla_gnss_event: carla gnss event object
        :type carla_gnss_event: carla.GnssEvent
        """
        navsatfix_msg = NavSatFix()
        navsatfix_msg.header = self.get_msg_header(timestamp=carla_gnss_event.timestamp)
        navsatfix_msg.latitude = carla_gnss_event.latitude
        navsatfix_msg.longitude = carla_gnss_event.longitude
        navsatfix_msg.altitude = carla_gnss_event.altitude
        self.publish_message(
            self.get_topic_prefix() + "/fix", navsatfix_msg)



#https://github.com/carlasia/carla/blob/043e718e1e3149dde80f75003cb14d79001327cf/PythonAPI/carla/scene_layout.py   
 def get_vehicles(vehicles):
        vehicles_dict = dict()
        for vehicle in vehicles:
            v_transform = vehicle.get_transform()
            location_gnss = carla_map.transform_to_geolocation(v_transform.location)
            v_dict = {
                "id": vehicle.id,
                "position": [location_gnss.latitude, location_gnss.longitude, location_gnss.altitude],
                "orientation": [v_transform.rotation.roll, v_transform.rotation.pitch, v_transform.rotation.yaw],
                "bounding_box": [[v.longitude, v.latitude, v.altitude] for v in _get_bounding_box(vehicle)]
            }
            vehicles_dict[vehicle.id] = v_dict
        return vehicles_dict



# Help function in the development
def print_location(data):
    print(data.latitude, data.longitude)


# Initialise the situation by spawning the car and GNSS sensor at a set location

def set_up():
    try:

        # ...
        client = carla.Client("localhost", 2000)
        client.set_timeout(2.0)
        world = client.get_world()
        spectator = world.get_spectator()
        bp_library = world.get_blueprint_library()
        map = world.get_map()

        vehicle_bp = random.choice(bp_library.filter('vehicle.bmw.grandtourer'))
        print(vehicle_bp)
        transform = carla.Transform(carla.Location(87.1881,-86.9629,9.84228),carla.Rotation(0,-90,0))
        transform_spec = carla.Transform(spectator.get_location(),carla.Rotation(0,-90,0))
        vehicle = world.try_spawn_actor(vehicle_bp, transform)

        # Wait for world to get the vehicle actor
        world.tick()

        spec_transform = transform   # spec_transform location defined for spectator position
        spec_transform.location.z += 1
        spec_transform.location.y += 5

        # Set spectator at given transform (vehicle transform)
        spectator.set_transform(spec_transform)
        #vehicle.apply_control(carla.VehicleControl(throttle=0.5, steer=0.0))

        world.tick()

        # Create gnss sensor actor on top of the vehicle (vehicle transform).
        gnss_bp = random.choice(bp_library.filter('gnss'))
        gnss = world.try_spawn_actor(gnss_bp, transform, attach_to=vehicle)


        # ...
        return vehicle, gnss

    finally:
        pass