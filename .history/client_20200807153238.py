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
            return port['value']

def print_data_by_actor_and_port_name():
    
async def start():
    uri = "ws://192.168.114.18:8887"
    actor_info = {
        'clazz' : '',
        'name' : '',
        'uuid' : None,
        'parent_uuid' : None
    }
    
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
            # name = f"luman!"
            # await websocket.send(name)
            # #print(f"> {name}")
            #await sendmessage(websocket)
            gunnerus = None
            ts1 = None
            ts2 = None
            if not websocket.open:
                print('reconnecting')
                websocket = await websockets.connect(uri)
            else:
                resp = await websocket.recv()                
                #print(f"{resp}")
                for i in range(len(actor_list)):
                    actor_info = actor_info_list[i]
                    actor = await evaluate(resp, actor_info['clazz'], actor_info['name'])
                    if actor != None:
                        actor_info['uuid'] = actor['uuid']
                        actor_info['parent_uuid'] = get_port_value_by_name(actor['output'],'PARENT')
                
                # actor1 = await evaluate(resp, 'GPSController', 'GPS1')
                # if actor1 != None:
                #     clazz_ls(actor1) # gunnerus
                # actor2  = await evaluate(resp, 'ThrusterActor', 'Port')
                # if actor2 != None:
                #     clazz_ls(actor2)
                # actor3  = await evaluate(resp, 'ThrusterActor', 'Starboard')
                # if actor3 != None:
                #     #print(actor3)
                #     clazz_ls(actor3)    
                # actor4 = await evaluate(resp, 'GPSController', 'Target Ship 1')
                # if actor4 != None:
                #     clazz_ls(actor4) # ts1 = actor2
                # actor5 = await evaluate(resp, 'GPSController', 'Target Ship 2')
                # if actor5 != None:
                #     clazz_ls(actor5) # ts2 = actor3
                # actor5  = await evaluate(resp, 'ThrusterActor', 'Starboard')
                # if actor4 != None:
                    #print(actor5)
                    #clazz_ls(actor5)
                    
            # await sendmessage()
            
# async def sendmessage():
#     name = f"luman"
#     return websocket.send(name)

async def evaluate(receivedata, clazz, name):
    try:
        data_dic = json.loads(receivedata[receivedata.index('{'):])
        # print(data_dic)
        # time.sleep(100)
        # data_str = json.dumps(data_dic, indent=4, sort_keys=True)
        x = False if data_dic['clazz'].find(clazz) == -1 else True 
        y = (data_dic['name'] == name)
        if x and y:
            return data_dic
    except:
        traceback.print_exc()

def clazz_ls(data_dic):
    #print(data_dic['output']) # list
    lon, lat, east, north, course, speed, rpm, alpha = 0.0, 0.0, 0.0, 0.0, 0.0, [], 0.0, 0.0
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
