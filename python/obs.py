'''
Interface with OBS via websockets

A connection daemon checks the websocket connection every second

If disconnected from OBS, all methods do nothing while connection is reestablished in the daemon thread
'''

import obsws_python
import threading
import time
import numpy as np

class OBS():
  
  def __init__(self, password, host='localhost', port=4455, verbose=False):
    '''
    @param password OBS websocket password set in OBS app settings
    '''
    self.host = host
    self.port = port
    self.password = password
    self.verbose = verbose

    # Create list of values to increment volume slider
    self.lvls = np.logspace(0, 2, 20)
    self.lvls = np.insert(self.lvls, 0, 0)
    
    # websocket objects
    self.request = None
    self.event = None
    
    self.scenes = []
    self.scene_index = -1

    self.mic_name = ''
    self.volume = 1
    self.is_muted = False

    self.is_streaming = False
    self.is_recording = False

    fn = lambda _: None
    self.on_scene_change = fn
    self.on_stream_change = fn
    self.on_record_change = fn
    self.on_mute_change = fn

    self.connect()

    threading.Thread(target=self.check_connection, daemon=True).start()

  # -------------------- Websocket connection methods --------------------

  def connect(self):
    '''
    Connect to OBS websocket
    Register any callbacks that have already been attempted to be registered
    '''
    try:
      self.request = obsws_python.ReqClient(host=self.host, port=self.port, password=self.password)
      self.event = obsws_python.EventClient(host=self.host, port=self.port, password=self.password)

      self.get_scenes()
      self.get_outputs()
      self.get_input()

      # register any callbacks
      self.register_on_scene_change(self.on_scene_change)
      self.register_on_stream_change(self.on_stream_change)
      self.register_on_record_change(self.on_record_change)
      self.register_on_mute_change(self.on_mute_change)

      if self.verbose: print('Connected to OBS')

    except:
      self.request, self.event = None, None
      if self.verbose: print('Could not connect to OBS')

  def check_connection(self, t=1):
    '''
    Daemon thread that checks for connection every t seconds and reestablishes a lost connection
    '''
    while True:
      try: self.request.get_version()
      except: self.connect()
      time.sleep(t)

  # -------------------- OBS Scene methods --------------------

  def get_scene_index(self, scene_name):
    '''
    @return scene index for a given scene_name in the current scene list else -1 if not found
    '''
    for s in self.scenes:
      if s['scene_name'] == scene_name: return s['scene_index']
    return -1

  def get_scenes(self):
    '''
    Update the current scene index and current scene list
    @return scene_index, scenes
    '''
    try:
      scenes = self.request.get_scene_list().scenes
      scene_name = self.request.get_current_program_scene().current_program_scene_name
    except:
      return self.scene_index, self.scenes

    # reverse indices and convert to snake_case
    for s in scenes:
      s['scene_index'] = len(scenes) - s['sceneIndex'] - 1
      s['scene_name'] = s['sceneName']

    self.scenes = sorted(scenes, key=lambda s: s['scene_index'])
    self.scene_index = self.get_scene_index(scene_name)

    return self.scene_index, self.scenes # also return them
  
  def set_scene(self, scene_index):
    '''
    Request OBS change scene to scene_index
    @return scene_index if successful else -1
    '''
    self.get_scenes()
    try:
      scene_name = self.scenes[scene_index]['scene_name']
      self.request.set_current_program_scene(scene_name)

      if self.verbose: print(f'Switched to {scene_name}')
      return scene_index
    
    except: return -1

  # -------------------- OBS Audio methods --------------------

  def get_input(self):
    try:
      req = self.request.get_input_list().inputs
      inputs = [volume for volume in req if volume['inputKind'] in ('wasapi_input_capture', 'coreaudio_input_capture')]
      
      self.mic_name = inputs[0]['inputName']
      self.volume = self.request.get_input_volume(self.mic_name).input_volume_db
      self.is_muted = self.request.get_input_mute(self.mic_name).input_muted

    except Exception as e: pass
    return self.volume

  def toggle_mute(self):
    try: self.request.toggle_input_mute(self.mic_name)
    except Exception as e: pass

  def set_volume(self, vol_db):
    try:
      vol_db = int(vol_db)
      index = int(-int(vol_db)/5)
      actual_vol_db = -self.lvls[index]
      self.request.set_input_volume(self.mic_name, vol_db=actual_vol_db)
      self.volume = vol_db
    except Exception as e: pass
    return self.volume

  # -------------------- OBS Stream/recording methods --------------------

  def get_outputs(self):
    try:
      self.is_streaming = self.request.get_stream_status().output_active
      self.is_recording = self.request.get_record_status().output_active
    except Exception as e: pass

  def toggle_stream(self):
    try: self.request.toggle_stream()
    except Exception as e: pass


  def toggle_record(self):
    try: self.request.toggle_record()
    except Exception as e: pass

  # -------------------- Register event callbacks --------------------

  def register_on_scene_change(self, callback):
    '''
    Register a callback function on scene change that takes current scene_index as parameter
    Updates scene list before callback
    @param callback eg. def callback(scene_index): pass
    '''

    # store callback to be registered on reconnect
    self.on_scene_change = callback
  
    def on_current_program_scene_changed(data):
      self.get_scenes()
      callback(self.scene_index)

    # should also register the same callback on sceneListChanged 
    # however websockets does not support callback on scene reordering yet
    def on_scene_list_changed(data):
      on_current_program_scene_changed(data)

    try:
      self.event.callback.register(on_current_program_scene_changed)
      self.event.callback.register(on_scene_list_changed)
    except Exception as e: pass

  def register_on_stream_change(self, callback):
    '''
    Register a callback function on stream state change that takes is_streaming as a parameter
    @param callback eg. def callback(is_streaming): pass
    '''

    self.on_stream_change = callback

    def on_stream_state_changed(data):
      if data.output_state in ['OBS_WEBSOCKET_OUTPUT_STARTED', 'OBS_WEBSOCKET_OUTPUT_STOPPED']:
        self.is_streaming = data.output_state == 'OBS_WEBSOCKET_OUTPUT_STARTED'
        callback(self.is_streaming)

    try: self.event.callback.register(on_stream_state_changed)
    except Exception as e: pass
  
  def register_on_record_change(self, callback):
    self.on_record_change = callback
    def on_record_state_changed(data):
      if data.output_state in ['OBS_WEBSOCKET_OUTPUT_STARTED', 'OBS_WEBSOCKET_OUTPUT_STOPPED']:
        self.is_recording = data.output_state == 'OBS_WEBSOCKET_OUTPUT_STARTED'
        callback(self.is_recording)

    try: self.event.callback.register(on_record_state_changed)
    except Exception as e: pass

  def register_on_mute_change(self, callback):
    '''
    Register a callback function on mute state change that takes is_muted as a parameter
    @param callback eg. def callback(is_muted: bool): pass
    '''

    self.on_mute_change = callback

    def on_input_mute_state_changed(data):
      self.get_input()
      callback(self.is_muted)

    try: self.event.callback.register(on_input_mute_state_changed)
    except Exception as e: pass

# --------------------------------------------------

if __name__ == '__main__':
  from dotenv import dotenv_values

  env = dotenv_values()

  obs = OBS(env['OBS_PASSWORD'], verbose=True)
  obs.register_on_scene_change(lambda scene_index: print(f'Changed to {scene_index}'))

  while True:
    time.sleep(1)
    # obs.get_scenes()
    # print(obs.scene_index)
