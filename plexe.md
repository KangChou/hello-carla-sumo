if 'SUMO_HOME' in os.environ:
   tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
   sys.path.append(tools)
else:
   sys.exit("please declare environment variable 'SUMO_HOME'")
import traci
from plexe import Plexe, ACC, CACC, RPM, GEAR, RADAR_DISTANCE
# vehicle length
LENGTH = 4
# inter-vehicle distance
DISTANCE = 5
# platoon size
PLATOON_SIZE = 8
# number of platoon
PLATOON_NUM = 1
# cruising speed
SPEED = 33 # m/s
# distance between multiple platoons
PLATOON_DISTANCE = SPEED * 1.5 + 2
# vehicle who starts to brake
BRAKING_VEHICLE = "v.0.0"
# the original leader ID
ORI_LEADER_ID ="v.0.0"
# traffic light ID
TL_ID = "tl_0"
# range of traffic light broadcast
RANGE = 100 
# traffic light position
TL_POS = 558

def add_vehicles(plexe, n, n_platoons, real_engine=False):
 """
 Adds a set of platoons of n vehicles each to the simulation
 :param plexe: API instance
 :param n: number of vehicles of the platoon
 :param n_platoons: number of platoons
 :param real_engine: set to true to use the realistic engine model,
 false to use a first order lag model
 :return: returns the topology of the platoon, i.e., a dictionary which
 indicates, for each vehicle, who is its leader and who is its front
 vehicle. The topology can the be used by the data exchange logic to
 automatically fetch data from leading and front vehicle to feed the CACC
 """
 # add a platoon of n vehicles
     topology = {}
     p_length = n * LENGTH + (n - 1) * DISTANCE
     for p in range(n_platoons):
        for i in range(n):
           vid = "v.%d.%d" % (p, i)
           add_platooning_vehicle(plexe, vid, 200 + (n-i+1) * (DISTANCE+LENGTH), 0, SPEED, DISTANCE, real_engine)
           plexe.set_fixed_lane(vid, 0, False)
           traci.vehicle.setSpeedMode(vid, 0)
           plexe.use_controller_acceleration(vid, False)
           if i == 0:
               plexe.set_active_controller(vid, ACC)
           else:
               plexe.set_active_controller(vid, CACC)
           if i > 0:
               topology[vid] = {"front": "v.%d.%d" % (p, i - 1),  "leader": "v.%d.0" % p}
           else:
           topology[vid] = {}
     return topology
def main(demo_mode, real_engine, setter=None):
     # used to randomly color the vehicles
     random.seed(1)
     start_sumo("cfg/intersection/intersection.sumo.cfg", False)
     plexe = Plexe()
     traci.addStepListener(plexe)
     step = 0
     topology = dict()
     min_dist = 1e6
     split = False
     while running(demo_mode, step, 3000):
         traci.simulationStep()
         if step == 0:
             # create vehicles and track the braking vehicle
             topology = add_vehicles(plexe, PLATOON_SIZE, PLATOON_NUM, real_engine)
             tracked_veh = "v.0.%d" %(PLATOON_SIZE-1)
             traci.gui.trackVehicle("View #0", tracked_veh)
             traci.gui.setZoom("View #0", 2000)
         # when the leader is 100m away from the traffic light, it will receive the current phase of the traffic light
         # Accordingly, it computes which vehicles could pass safely.
         leader_data = plexe.get_vehicle_data(ORI_LEADER_ID)
         # the structure of vehicle data is defined in vehicle_data.py file in plexe folder
         # self.acceleration,  self.speed, self.pos_x, self.pos_y 
         if leader_data.pos_x >= TL_POS - RANGE and not split:
             current_phase = traci.trafficlight.getPhase(TL_ID)
             if current_phase == 0:
                 absolute_time = traci.trafficlight.getNextSwitch(TL_ID)
                 time_left = absolute_time - traci.simulation.getTime()
                 new_leader = floor((leader_data.speed * time_left - RANGE)/(LENGTH + DISTANCE))
                 new_leader_id = "v.0.%d" % new_leader
                 # change topology: add new leader and decelerate.
                 for i in range(new_leader+1,PLATOON_SIZE):
                 topology["v.0.%d" %i]["leader"] = new_leader_id
                 topology[new_leader_id] = {}
                 new_leader_data = plexe.get_vehicle_data(new_leader_id)
                 decel = new_leader_data.speed**2 / (2* (RANGE + new_leader * (LENGTH + DISTANCE)))
                 plexe.set_fixed_acceleration(new_leader_id, True, -1 * decel)
              split = True
         # set color for leader
         for i in range(PLATOON_SIZE):
             vid = "v.0.%d" % i
             if topology[vid] == {}:
                 traci.vehicle.setColor(vid, (250,0,0, 255))
         if step % 10 == 1:
             # simulate vehicle communication every 100 ms
             communicate(plexe, topology)
         if real_engine and setter is not None:
             # if we are running with the dashboard, update its values
             tracked_id = traci.gui.getTrackedVehicle("View #0")
             if tracked_id != "":
                 ed = plexe.get_engine_data(tracked_id)
                 vd = plexe.get_vehicle_data(tracked_id)
                 setter(ed[RPM], ed[GEAR], vd.speed, vd.acceleration)
         if split == True:
               new_leader_data = plexe.get_vehicle_data(new_leader_id)
               current_phase = traci.trafficlight.getPhase(TL_ID)
               if TL_POS - new_leader_data.pos_x < 10 and current_phase == 0: 
                   plexe.set_fixed_acceleration(new_leader_id, True, 3)
         if step > 1:
               radar = plexe.get_radar_data("v.0.1")
               if radar[RADAR_DISTANCE] < min_dist:
                     min_dist = radar[RADAR_DISTANCE]
         step += 1
         if step > 3000:
             break
     traci.close()
if __name__ == "__main__":
 main(True, True)
























import os
import sys
import random
from utils import add_platooning_vehicle, communicate, get_distance, \
    start_sumo, running


if 'SUMO_HOME' in os.environ:
   tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
   sys.path.append(tools)
else:
   sys.exit("please declare environment variable 'SUMO_HOME'")
import traci
from plexe import Plexe, ACC, CACC, RPM, GEAR, RADAR_DISTANCE
# vehicle length
LENGTH = 4
# inter-vehicle distance
DISTANCE = 5
# platoon size
PLATOON_SIZE = 8
# number of platoon
PLATOON_NUM = 1
# cruising speed
SPEED = 33 # m/s
# distance between multiple platoons
PLATOON_DISTANCE = SPEED * 1.5 + 2
# vehicle who starts to brake 开始刹车的车辆
BRAKING_VEHICLE = "v.0.0"
# the original leader ID 原领导ID
ORI_LEADER_ID ="v.0.0"
# traffic light ID
TL_ID = "tl_0"
# range of traffic light broadcast
RANGE = 100 
# traffic light position
TL_POS = 558

def add_vehicles(plexe, n, n_platoons, real_engine=False):

 """
 Adds a set of platoons of n vehicles each to the simulation
 :param plexe: API instance
 :param n: number of vehicles of the platoon
 :param n_platoons: number of platoons
 :param real_engine: set to true to use the realistic engine model,
 false to use a first order lag model
 :return: returns the topology of the platoon, i.e., a dictionary which
 indicates, for each vehicle, who is its leader and who is its front
 vehicle. The topology can the be used by the data exchange logic to
 automatically fetch data from leading and front vehicle to feed the CACC
 """
 # add a platoon of n vehicles
    topology = {}
     p_length = n * LENGTH + (n - 1) * DISTANCE
     for p in range(n_platoons):
        for i in range(n):
           vid = "v.%d.%d" % (p, i)
           add_platooning_vehicle(plexe, vid, 200 + (n-i+1) * (DISTANCE+LENGTH), 0, SPEED, DISTANCE, real_engine)
           plexe.set_fixed_lane(vid, 0, False)
           traci.vehicle.setSpeedMode(vid, 0)
           plexe.use_controller_acceleration(vid, False)
           if i == 0:
               plexe.set_active_controller(vid, ACC)
           else:
               plexe.set_active_controller(vid, CACC)
           if i > 0:
               topology[vid] = {"front": "v.%d.%d" % (p, i - 1),  "leader": "v.%d.0" % p}
           else:
           topology[vid] = {}
     return topology
def main(demo_mode, real_engine, setter=None):
     # used to randomly color the vehicles
     random.seed(1)
     start_sumo("cfg/intersection/intersection.sumo.cfg", False)
     plexe = Plexe()
     traci.addStepListener(plexe)
     step = 0
     topology = dict()
     min_dist = 1e6
     split = False
     while running(demo_mode, step, 3000):
         traci.simulationStep()

         #这里只是视角调整环节
         if step == 0:
             # create vehicles and track the braking vehicle
             # 创建车辆并跟踪制动车辆
             topology = add_vehicles(plexe, PLATOON_SIZE, PLATOON_NUM, real_engine)
             tracked_veh = "v.0.%d" %(PLATOON_SIZE-1)
             traci.gui.trackVehicle("View #0", tracked_veh)
             traci.gui.setZoom("View #0", 2000)
         
         # when the leader is 100m away from the traffic light, it will receive the current phase of the traffic light
         # Accordingly, it computes which vehicles could pass safely.
         #当引线距离红绿灯100m时，接收当前相位的红绿灯
         #因此，它计算出哪些车辆可以安全通过。
         leader_data = plexe.get_vehicle_data(ORI_LEADER_ID)
         # the structure of vehicle data is defined in vehicle_data.py file in plexe folder
         # 车辆数据的结构在车辆中定义_数据.pyplexe文件夹中的文件
         # self.acceleration,  self.speed, self.pos_x, self.pos_y 
         if leader_data.pos_x >= TL_POS - RANGE and not split:
             current_phase = traci.trafficlight.getPhase(TL_ID)  #相位信息  TL_ID为交通灯的id
             if current_phase == 0:
                 absolute_time = traci.trafficlight.getNextSwitch(TL_ID)
                 time_left = absolute_time - traci.simulation.getTime()
                 new_leader = floor((leader_data.speed * time_left - RANGE)/(LENGTH + DISTANCE))
                 new_leader_id = "v.0.%d" % new_leader
                 # change topology: add new leader and decelerate.  #改变车辆拓扑
                 for i in range(new_leader+1,PLATOON_SIZE):
                 topology["v.0.%d" %i]["leader"] = new_leader_id
                 topology[new_leader_id] = {}
                 new_leader_data = plexe.get_vehicle_data(new_leader_id)
                 decel = new_leader_data.speed**2 / (2* (RANGE + new_leader * (LENGTH + DISTANCE)))
                 plexe.set_fixed_acceleration(new_leader_id, True, -1 * decel)
              split = True
         # set color for leader  #给领航车辆加上颜色
         for i in range(PLATOON_SIZE):
             vid = "v.0.%d" % i
             if topology[vid] == {}:
                 traci.vehicle.setColor(vid, (250,0,0, 255))
        

         if step % 10 == 1:
             # simulate vehicle communication every 100 ms
             communicate(plexe, topology)
         if real_engine and setter is not None:
             # if we are running with the dashboard, update its values
             tracked_id = traci.gui.getTrackedVehicle("View #0")
             if tracked_id != "":
                 ed = plexe.get_engine_data(tracked_id)
                 vd = plexe.get_vehicle_data(tracked_id)
                 setter(ed[RPM], ed[GEAR], vd.speed, vd.acceleration)
         
         # 交通灯
         if split == True:
               new_leader_data = plexe.get_vehicle_data(new_leader_id)
               current_phase = traci.trafficlight.getPhase(TL_ID)
               if TL_POS - new_leader_data.pos_x < 10 and current_phase == 0: 
                   plexe.set_fixed_acceleration(new_leader_id, True, 3)
         

         if step > 1:
               radar = plexe.get_radar_data("v.0.1")
               if radar[RADAR_DISTANCE] < min_dist:
                     min_dist = radar[RADAR_DISTANCE]
         step += 1
         if step > 3000:
             break
     traci.close()
if __name__ == "__main__":
 main(True, True)
