import asyncio
import websockets
import time
import json
import traceback
import argparse
import rospy

async def start():
    uri = "ws://192.168.114.18:8887"
    async with websockets.connect(uri, ping_timeout=None) as websocket:
        while True:
            # name = f"luman!"
            # await websocket.send(name)
            # #print(f"> {name}")
            if not websocket.open:
                print('reconnecting')
                websocket = await websockets.connect(uri)
            else:
                resp = await websocket.recv()                
                #print(f"{resp}")
                await evaluate(resp)
                

async def evaluate(receivedata):
    try:
        data_dic = json.loads(receivedata[receivedata.index('{'):])
        # print(data_dic)
        # time.sleep(100)
        # data_str = json.dumps(data_dic, indent=4, sort_keys=True)
        if data_dic["clazz"].find('GPSController'): 
            if data_dic["name"] == "GPS1":
                data = clazz_ls(data_dic)
                #print(data)
            elif data_dic["name"] == "Target Ship 1":
                data = clazz_ls(data_dic)
                print(data)
            elif data_dic["name"] == "Target Ship 2":
                data = clazz_ls(data_dic)
                print(data)
        elif data_dic["clazz"].find("TypedSixDOFActor"):     
            if data_dic["name"] == "Gunnerus":                
                data = clazz_ls(data_dic)
            elif data_dic["name"] == "Target Ship 1":
                data = clazz_ls(data_dic)
            elif data_dic["name"] == "Target Ship 2":
                data = clazz_ls(data_dic)
        elif data_dic["clazz"].find("ThrusterActor"):
            if data_dic["name"] == "Starboard":                
                data = clazz_ls(data_dic)
            elif data_dic["name"] == "Port":
                data = clazz_ls(data_dic)
            elif data_dic["name"] == "Tunnel":
                data = clazz_ls(data_dic)
        else:
            pass  
    except:
        traceback.print_exc()


def clazz_ls(data_dic):
    #print(data_dic['output']) # list
    lon, lat, east, north, course, speed = 0.0, 0.0, 0.0, 0.0, 0.0, []
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
        else:
            pass 
    all_data = [lon, lat, east, north, course, speed]     
    return all_data

async def savefile(receivedata):
    #time.sleep(5)
    with open('serverdata.json', 'w') as json_file:
        json_file.writelines(receivedata)

if __name__=='__main__':
    rospy.init_node("simulator_drl")
    asyncio.get_event_loop().run_until_complete(start())
    asyncio.get_event_loop().run_forever()
