from serial import Serial, STOPBITS_ONE
from obswebsocket import obsws, requests
from time import time

WRITE_DELAY = 0.5 # seconds
last_write_time = 0

serialPort = Serial(port="/dev/cu.usbserial-1410", baudrate=9600, bytesize=8, timeout=2, stopbits=STOPBITS_ONE)

host = "localhost"
port = 4455
password = "jasper01"

ws = obsws(host, port, password)
ws.connect()

scenes = ws.call(requests.GetSceneList()).getScenes()
currentName = ws.call(requests.GetCurrentProgramScene()).datain['currentProgramSceneName']
scene = [s['sceneIndex'] for s in scenes if s['sceneName'] == currentName][0]

try:
    while True:
        # button press
        if serialPort.in_waiting > 0:
            scene = int.from_bytes(serialPort.read(), "big")
            print(f'Switching to Scene {scene}')
            ws.call(requests.SetCurrentProgramScene(sceneName=scenes[scene]['sceneName']))

        # send current scene number to LEDs
        if time() - last_write_time > WRITE_DELAY:
            scenes = ws.call(requests.GetSceneList()).getScenes()
            currentName = ws.call(requests.GetCurrentProgramScene()).datain['currentProgramSceneName']
            scene = [s['sceneIndex'] for s in scenes if s['sceneName'] == currentName][0]

            serialPort.write(scene.to_bytes(1, "big"))
            last_write_time = time()
        
except KeyboardInterrupt: ws.disconnect()