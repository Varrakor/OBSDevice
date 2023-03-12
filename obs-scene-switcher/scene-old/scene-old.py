from serial import Serial, STOPBITS_ONE
from obswebsocket import obsws, requests

serialPort = Serial(port="/dev/cu.usbserial-1410", baudrate=9600, bytesize=8, timeout=2, stopbits=STOPBITS_ONE)
scene = 0

host = "localhost"
port = 4455
password = "jasper01"

ws = obsws(host, port, password)
ws.connect()

scenes = ws.call(requests.GetSceneList()).getScenes()

try:
    while True:
        
        # read button press
        if serialPort.in_waiting > 0:
            s = int.from_bytes(serialPort.read(), "big")
            ws.call(requests.SetCurrentProgramScene(sceneName=scenes[s]['sceneName']))
        
except KeyboardInterrupt: ws.disconnect()