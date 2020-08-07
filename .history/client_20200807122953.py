import asyncio
import websockets
import time
import json
import traceback

async def start():
    uri = "ws://192.168.114.18:8887"
    # counter1 = 0
    # counter2 = 0
    # counter3 = 0
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
                actor1 = await evaluate(resp, 'GPSController', 'GPS1')
                if actor1 != None:
                    clazz_ls(actor1) # gunnerus
                actor2 = await evaluate(resp, 'GPSController', 'Target Ship 1')
                if actor2 != None:
                    clazz_ls(actor2) # ts1 = actor2
                actor3 = await evaluate(resp, 'GPSController', 'Target Ship 2')
                if actor3 != None:
                    clazz_ls(actor3) # ts2 = actor3
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
    print(all_data)

async def savefile(receivedata):
    #time.sleep(5)
    with open('serverdata.json', 'w') as json_file:
        json_file.writelines(receivedata)

if __name__=='__main__':
    #rospy.init_node("simulator_drl")
    asyncio.get_event_loop().run_until_complete(start())
    asyncio.get_event_loop().run_forever()
