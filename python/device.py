'''Interface with the physical device via serial'''

import obs
import ppt
import serial
import serial.tools.list_ports
import time

class DeviceInterface():
  
  def __init__(self, obs_host='localhost', obs_port=obs.DEFAULT_PORT, obs_password='', verbose=False):
    self.obs = obs.OBS(obs_host, obs_port, obs_password, verbose=verbose)
    
    self.obs.register_on_scene_change(lambda scene_index: self.send_current_scene(scene_index))
    self.obs.register_on_stream_change(lambda is_streaming: self.send_output_state(is_streaming))
    self.obs.register_on_record_change(lambda is_recording: self.send_output_state(is_recording))
    self.obs.register_on_mute_change(lambda is_muted: self.send_mute_state(is_muted))

    self.auto_detect = True
    self.serial_ports = []

    self.serial_port = ''
    self.serial = None

    self.verbose = verbose
    
    self.connect_callback = lambda: None
    self.disconnect_callback = lambda: None

    self.connected = False
    self.connect()

  @staticmethod
  def is_usb(port):
    return 'usbserial' in port.device or 'USB-SERIAL' in port.description

  def get_ports(self):
    self.serial_ports = [p for p in serial.tools.list_ports.comports(include_links=False) if self.is_usb(p)]
    return self.serial_ports
  
  def set_port(self, name):
    self.serial_port = name

  def auto_set_port(self):
    '''choose first serial port that matches the usb criteria'''
    self.get_ports()
    if self.serial_ports:
      self.serial_port = self.serial_ports[0].device

  def connect(self):
    try:
      if self.auto_detect: self.auto_set_port()
      if not self.serial_port: raise Exception('Could not detect serial port.')

      self.serial = serial.Serial(self.serial_port, baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
      if self.serial: print(f'Connected to {self.serial_port}')
      
      self.connected = True
      self.connect_callback()

      time.sleep(2) # wait for controller to reset should be non blocking
      self.send_current_scene(self.obs.scene_index) # send current scene to leds
      self.send_output_state(self.obs.is_streaming or self.obs.is_recording)
      self.send_mute_state(self.obs.is_muted)
    
    except KeyboardInterrupt: exit()
    except Exception as e:
      time.sleep(1) # should be non blocking
      if self.verbose: print(e)

      self.serial = None
      self.connected = False
      self.disconnect_callback()

  def send_current_scene(self, scene_index):
    try:
      if scene_index >= 0 and scene_index < 8:
        self.serial.write(int.to_bytes(scene_index, 1, 'big'))

    except KeyboardInterrupt: exit()
    except: self.connect()

  def send_output_state(self, is_started):
    try:
      if is_started: self.serial.write(int.to_bytes(8, 1, 'big')) # 8 represents output started
      else: self.serial.write(int.to_bytes(9, 1, 'big')) # 9 represents output stopped
    
    except KeyboardInterrupt: exit()
    except: self.connect()

  def send_mute_state(self, is_muted):
    if is_muted: self.serial.write(int.to_bytes(10, 1, 'big')) # 10 is muted
    else: self.serial.write(int.to_bytes(11, 1, 'big')) # 11 is unmuted

  def decrement_volume(self):
    self.obs.get_input()
    self.obs.decrement_volume()

  def increment_volume(self):
    self.obs.get_input()
    self.obs.increment_volume()

  def poll(self):
    try:
      if self.serial.in_waiting > 0:
        key = int.from_bytes(self.serial.read(), 'big')
        print(key)
        
        if key >= 0 and key <= 7: self.obs.set_scene(key)

        elif key == 8: self.obs.toggle_stream()
        elif key == 9: self.obs.toggle_record()
        elif key == 10: self.obs.toggle_mute()
        
        elif key == 11: ppt.previous_slide()
        elif key == 12: ppt.next_slide()

        elif key == 13: self.decrement_volume()
        elif key == 14: self.increment_volume()
            
    except KeyboardInterrupt: exit()
    except: self.connect()

  def loop(self):
    '''
    Input:
    key 0-7  scenes
    key 8, 9, 10 toggle stream/recording/mute
    key 11, 12 prev/next slide
    key 13, 14 rotor decrement/increment

    Output:
    key 0-7 current scene led
    key 8 output started
    key 9 output stopped
    key 10 muted
    key 11 unmuted
    '''
    while True: self.poll()

if __name__ == '__main__':
  from dotenv import dotenv_values
  import sys
  env = dotenv_values()
  
  d = DeviceInterface(obs_password=env['OBS_PASSWORD'], verbose=len(sys.argv) > 1)
  d.loop()