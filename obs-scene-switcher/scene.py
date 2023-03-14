from serial import Serial, STOPBITS_ONE
from obswebsocket import obsws, requests
from time import time
from dotenv import dotenv_values

DELAY = 0.5 # seconds
last_write_time = 0

env = dotenv_values()

def get_scenes():
    """
    returns a tuple (list of scenes, current scene number)
    """
    scenes = ws.call(requests.GetSceneList()).getScenes()
    currentName = ws.call(requests.GetCurrentProgramScene()).datain['currentProgramSceneName']
    scene = [s['sceneIndex'] for s in scenes if s['sceneName'] == currentName][0]
    return scenes, scene

if __name__ == '__main__':

    obs_connect, remote_connect = False, False

    # loop until connected to obs and remote
    while True:
        if not obs_connect:
            try:
                ws = obsws(env['HOST'], env['PORT'], env['PASSWORD'])
                ws.connect()
                print('Connected to OBS')
                obs_connect = True
            except KeyboardInterrupt: exit()
            except: pass

        if not remote_connect:
            try:
                serialPort = Serial(env['SERIAL_PORT'], baudrate=9600, bytesize=8, timeout=2, stopbits=STOPBITS_ONE)
                print('Connected to remote device')
                remote_connect = True
            except KeyboardInterrupt: exit()
            except: pass

        if obs_connect and remote_connect: break

    scenes, scene = get_scenes()
    
    try:
        while True:
            # handle button press
            if serialPort.in_waiting > 0:
                scenes, oldScene = get_scenes()
                scene = int.from_bytes(serialPort.read(), "big")
                if scene < len(scenes):
                    sceneName = scenes[scene]['sceneName']
                    if scene != oldScene: print(f'Switching to {sceneName}')
                    ws.call(requests.SetCurrentProgramScene(sceneName=sceneName))
                    
            # send current scene number to LEDs after DELAY seconds
            if time() - last_write_time > DELAY:
                scenes, scene = get_scenes()
                serialPort.write(scene.to_bytes(1, "big"))
                last_write_time = time()
            
    except KeyboardInterrupt: pass
    except Exception as e: print(e)

    ws.disconnect()