'''Interface with the physical device via serial'''

from obs import OBS
import ppt
import serial
import serial.tools.list_ports
import time

class DeviceInterface():
  
  def __init__(self, obs_password, obs_host='localhost', obs_port=4455, serial_port=None):
    self.obs = OBS(obs_password, obs_host, obs_port)
    
    self.obs.register_on_scene_change(lambda scene_index: self.send_current_scene(scene_index))
    self.obs.register_on_stream_change(lambda output_state: self.send_output_state(output_state))
    self.obs.register_on_record_change(lambda output_state: self.send_output_state(output_state))

    self.serial = None
    self.serial_port = serial_port

    self.connect()

  def detect_port(self):
    ports = serial.tools.list_ports.comports(include_links=False)
    for port in ports:
        if 'usbserial' in port.device:
          self.serial_port = port.device

  def connect(self):
    if not self.serial_port: self.detect_port()
    try:
      self.serial = serial.Serial(self.serial_port, baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
      if self.serial: print(f'Connected to {self.serial_port}')

      time.sleep(2) # wait for controller to reset
      self.send_current_scene(self.obs.scene_index) # send current scene to leds
    
    except KeyboardInterrupt: exit()
    except: self.serial = None

  def send_current_scene(self, scene_index):
    '''
    Callback on scene change, to be set in the obs object
    '''
    try:
      if scene_index >= 0 and scene_index < 8:
        self.serial.write(int.to_bytes(scene_index, 1, 'big'))

    except KeyboardInterrupt: exit()
    except: self.connect()

  def send_output_state(self, output_state):
    try:
      if output_state == OBS.OUTPUT_STARTED:
        self.serial.write(int.to_bytes(8, 1, 'big')) # 8 represents output started
      elif output_state == OBS.OUTPUT_STOPPED:
        self.serial.write(int.to_bytes(9, 1, 'big')) # 9 represents output stopped
    
    except KeyboardInterrupt: exit()
    except: self.connect()

  def loop(self):
    '''
    key 0 - 7  scene numbers to switch to
    key 8, 9  toggle stream and recording
    key 10, 11 change slide to previous and next
    '''
    while True:
      try:
        if self.serial.in_waiting > 0:
          key = int.from_bytes(self.serial.read(), 'big')
          
          if key >= 0 and key <= 7: self.obs.set_scene(key)

          elif key == 8: self.obs.toggle_stream()
          elif key == 9: self.obs.toggle_record()

          elif key == 10: ppt.change_slide(ppt.PREVIOUS)
          elif key == 11: ppt.change_slide(ppt.NEXT)
          
      except KeyboardInterrupt: exit()
      except: self.connect()

if __name__ == '__main__':
  from dotenv import dotenv_values
  env = dotenv_values()
  DeviceInterface(env['OBS_PASSWORD']).loop()