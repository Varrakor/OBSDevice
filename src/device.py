'''Interface with the physical device via serial'''

from obs import OBS
import ppt
import serial
import serial.tools.list_ports

class DeviceInterface():
  
  def __init__(self, obs_password, serial_port=None, obs_host='localhost', obs_port=4455):
    self.obs = OBS(self.obs_password, self.obs_host, self.obs_port)
    self.serial = None

    self.serial_port = serial_port
    self.obs_password = obs_password
    self.obs_host = obs_host
    self.obs_port = obs_port

    self.connect()
    
  def connect(self):

    if not self.serial_port: # auto detect
      ports = serial.tools.list_ports.comports(include_links=False)
      for port in ports:
          if 'usbserial' in port.device:
            self.serial_port = port.device

    try:
      self.serial = serial.Serial(self.serial_port, baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
    except: pass

  def connected(self):
    return self.serial and self.serial.is_open() # need a way to gracefully disconnect and reconnect

  def loop(self):
    while True:
      if not self.connected():
        self.connect()
        continue

      if self.serial.in_waiting > 0:
        key = int.from_bytes(self.serial.read(), 'big')
        
        if key >= 0 and key < 8:
          self.obs.set_scene(key)

        elif key == 9: self.obs.toggle_stream()
        elif key == 10: self.obs.toggle_record()
        
        elif key == 11: ppt.change_slide(ppt.PREVIOUS)
        elif key == 12: ppt.change_slide(ppt.NEXT)

if __name__ == '__main__':
  from dotenv import dotenv_values
  env = dotenv_values()
  DeviceInterface(env['OBS_PASSWORD']).loop()