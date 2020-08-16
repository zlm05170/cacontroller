import asyncio
import websockets
import time
import json
import traceback
import itertools

def view_actor_data(actor, port_type, port_name):
    pass

def find_gps_port_value(actor, port_type, port_name_ls):
    port_list = actor[port_type]
    num_port = len(port_list)
    num_port_name = len(port_name_ls)
    speed = []
    gps_info = []
    for i in range(num_port_name): # 5,2
        for j in range(num_port): # 34, 34
            port_name = port_list[j]['port']['name']
            if port_name == port_name_ls[i]:
                if port_name == "WORLD_VELOCITY".upper():
                    value_ls = port_list[j]['value']['valueObjects']
                    for v in value_ls:
                        speed.append(v['value'])                                                      
                else:
                    gps_info.append(port_list[j]['value']['value'])
                    break 
    return gps_info, speed                                                                

def find_actuator_port_value(actor, port_type, port_name_ls):
    port_list = actor[port_type]
    num_port = len(port_list)
    num_port_name = len(port_name_ls)
    rudder, rpm = [], []
    for i in range(num_port_name): # 5, 2
        for j in range(num_port): # 34, 34
            port_name = port_list[j]['port']['name']
            if port_name == port_name_ls[i]:                                                      
                if port_name == "ANGLE".upper():
                    angle = port_list[j]['value']['value']
                    rudder.append(angle)
                elif port_name == "ACTUAL_RPM".upper():
                    velocity = port_list[j]['value']['value']
                    rpm.append(velocity)                            
    return rudder, rpm   

def ls_to_dic(receivedata, port_gps_info):
    num_port = len(receivedata)
    num_port_name = len(port_gps_info)
    result = dict()
    for i in range(0, num_port, num_port_name):
        for key, val in zip(port_gps_info,receivedata[i:i+num_port_name]):
            if key not in result:
                result[key] = []
            result[key].append(val)
    return result

async def start():
    uri = "ws://192.168.114.18:8887"
    actor_info = {
        'clazz' : '',
        'name' : '',
        'uuid' : None,
        'parent_uuid' : None
    }

    port_gps_info = {
        'clazzname': '',
        'LONGITUDE': None,
        'LATITUDE': None,
        'EASTING': None,
        'NORTHING': None,
        'BEARING': None,
        'WORLD_VELOCITY':[]
    }

    port_actuator_info = {
        'clazzname': '',
        'ANGLE': [], # starboard rudder, port rudder
        'ACTUAL_RPM': [] # starboard rpm, port rpm
    }

    port_gps_name_ls, port_actuator_name_ls  = [], []
    for name in port_gps_info:
        port_gps_name_ls.append(name)   
    port_gps_name_ls.pop(0) # port's name
    for name in port_actuator_info:
        port_actuator_name_ls.append(name)
    port_actuator_name_ls.pop(0)

    gps_gunnerus = actor_info.copy()
    gps_gunnerus['clazz'] = 'GPSController'
    gps_gunnerus['name'] = 'GPS1'

    gps_target_ship_1 = actor_info.copy()
    gps_target_ship_1['clazz'] = 'GPSController'
    gps_target_ship_1['name'] = 'Target Ship 1'

    gps_target_ship_2 = actor_info.copy()
    gps_target_ship_2['clazz'] = 'GPSController'
    gps_target_ship_2['name'] = 'Target Ship 2'

    gunnerus_thruster_port = actor_info.copy()
    gunnerus_thruster_port['clazz'] = 'ThrusterActor'
    gunnerus_thruster_port['name'] = 'Port'
    
    gunnerus_thruster_starboard = actor_info.copy()
    gunnerus_thruster_starboard['clazz'] = 'ThrusterActor'
    gunnerus_thruster_starboard['name'] = 'Starboard'

    actor_info_list = [gps_gunnerus, gps_target_ship_1, gps_target_ship_2, gunnerus_thruster_port, gunnerus_thruster_starboard]
    actor_list = [None for i in range(5)]
    actuator_json_list = [None for i in range(2)]

    async with websockets.connect(uri, ping_timeout=None) as websocket: 
        while True:
            if not websocket.open:
                print('reconnecting')
                websocket = await websockets.connect(uri)
            else:
                resp = await websocket.recv()                      
                try:
                    data_dic = json.loads(resp[resp.index('{'):])
                    #print(data_dic)
                    for i in range(len(actor_list)):
                        actor_info = actor_info_list[i]
                        actor = await evaluate_actor(data_dic, actor_info['clazz'], actor_info['name']) # dic                        
                        if actor != None:
                            if actor['name'] == 'Starboard': 
                                actuator_json = set_actuator_json(actor, 'input', 100) 
                            elif actor['name'] == 'Port':
                                actuator_json = set_actuator_json(actor, 'input', 100)
                                actuator_json_list.append(actuator_json)  
                                print(find_actuator_port_value(actor, 'output', port_actuator_name_ls))
                            else:
                                print(find_gps_port_value(actor, 'output', port_gps_name_ls))
                except:
                    traceback.print_exc()               
                websocket.send(actuator_json_list)

def set_actuator_json(actor, port_type, alpha):
    port_list = actor[port_type]
    num_port = len(port_list)
    for i in range(num_port):
        port_name = port_list[i]['port']['name']
        if port_name == "ANGLE".upper():
            port_list[i]['value']['value'] += 0.1 * alpha
        elif port_name == "ACTUAL_RPM".upper():
            port_list[i]['value']['value'] += 0.1 * alpha
    return actor

async def evaluate_actor(data_dic, clazz, name):       
    x = False if data_dic['clazz'].find(clazz) == -1 else True 
    y = (data_dic['name'] == name)
    if x and y:
        return data_dic     

async def savefile(receivedata):
    #time.sleep(5)
    with open('serverdata.json', 'w') as json_file:
        json_file.writelines(receivedata)

if __name__=='__main__':
    #rospy.init_node("simulator_drl")
    asyncio.get_event_loop().run_until_complete(start())
    asyncio.get_event_loop().run_forever()
