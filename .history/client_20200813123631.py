import asyncio
import websockets
import time
import json
import traceback

def view_actor_data(actor, port_type, port_name):
    pass
def get_port_value_by_name(port_list, name):
    for port in port_list:
        if port['port']['name'] == name:
            print("ok")
            #return port['value']

def find_port_index_by_name(actor, port_type, port_name):
    port_list = actor[port_type]
    num_port = len(port_list)
    for i in range(num_port):
        if port_list[i]['port']['name'] == port_name:
            return i

def get_port_data_by_index(actor, port_type, index):
    dic = actor[port_type][index]['port']['name'] + ':  ' + actor[port_type][index]['port']['value']['value']
    value = actor[port_type][index]['port']['value']['value']
    return dic, value
    #return dic

async def start():
    uri = "ws://192.168.114.18:8887"
    actor_info = {
        'clazz' : '',
        'name' : '',
        'uuid' : None,
        'parent_uuid' : None
    }

    port_info = {
        'clazzname': '',
        'Longitude': None,
        'latitude': None,
        'UTM East': None,
        'UTM North': None,
        'course': None,
        'speed':[],
        'rudderP': None,
        'rpmP': None,
        'rudderS': None,
        'rpmS': None
    }
    port_name_ls = []
    for name in port_info:
        port_name_ls.append(name) # port's name

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

    async with websockets.connect(uri, ping_timeout=None) as websocket:
        while True:
            if not websocket.open:
                print('reconnecting')
                websocket = await websockets.connect(uri)
            else:
                resp = await websocket.recv()
                #print(f"{resp}")                       
                try:
                    data_dic = json.loads(resp[resp.index('{'):])
                    for i in range(len(actor_list)):
                        actor_info = actor_info_list[i]
                        actor = await evaluate(data_dic, actor_info['clazz'], actor_info['name'])
                        if actor != None:
                            port_info['clazzname'] == actor_info['name']
                            for i in range(len(port_name_ls)):
                                index = find_port_index_by_name(actor, 'output', port_name_ls[i].upper())
                                dic, value = get_port_data_by_index(actor, 'output', index)
                                port_info[port_name_ls[i]] = value
                                
                except:
                    traceback.print_exc()               
        await sendmessage()
            
# async def sendmessage():
#     name = f"luman"
#     return websocket.send(name)

async def evaluate(data_dic, clazz, name):       
    x = False if data_dic['clazz'].find(clazz) == -1 else True 
    y = (data_dic['name'] == name)
    if x and y:
        return data_dic

def evaluate_port(actor, port_type, port_name): # port_name is the list of name of port
    #actor_info['uuid'] = actor['uuid']
    #print(actor_list)
    #actor_info['parent_uuid'] = get_port_value_by_name(actor['output'],'PARENT')
    port_ls = actor[port_type]
    for i in range(len(port_ls)):
        if port_ls[i]['port']['name'] == port_name:
            return 


def clazz_ls(data_dic):
    #print(data_dic['output']) # list
    lon, lat, east, north, course, speed, rpm, alpha = 0.0, 0.0, 0.0, 0.0, 0.0, [], [], []
    for message in data_dic['output']:
        port = message['port']['name']
        if port == "longitude".upper():
            lon = message['value']['value']
        elif port == "latitude".upper():
            lat = message['value']['value']
        elif port == "easting".upper():
            east = message['value']['value']
        elif port == "northing".upper():
            north = message['value']['value']
        elif port == "bearing".upper():
            course = message['value']['value']
        elif port == "WORLD_VELOCITY".upper():
            value_ls = message['value']['valueObjects']
            for v in value_ls:
                speed.append(v['value'])
        elif port == "ACTUAL_RPM".upper():
            rpm = message['value']['value']
        elif port == "ANGLE".upper():
            alpha = message['value']['value']
        else:
            pass 
    all_data = [lon, lat, east, north, course, speed, rpm, alpha]     
    #return all_data
    print(all_data)

async def savefile(receivedata):
    #time.sleep(5)
    with open('serverdata.json', 'w') as json_file:
        json_file.writelines(receivedata)

if __name__=='__main__':
    #rospy.init_node("simulator_drl")
    asyncio.get_event_loop().run_until_complete(start())
    asyncio.get_event_loop().run_forever()
