'''
Interface with OBS via websockets

A connection daemon checks the websocket connection every second

If disconnected from OBS, all methods do nothing while connection is reestablished in the daemon thread
'''

import obsws_python
import threading
import time

class OBS():

  # class variables
  OUTPUT_STARTED = True
  OUTPUT_STOPPED = False
  
  def __init__(self, password, host='localhost', port=4455, verbose=False):
    '''
    @param password OBS websocket password set in OBS app settings
    '''
    self.host = host
    self.port = port
    self.password = password
    self.verbose = verbose
    
    # websocket objects
    self.request = None
    self.event = None
    
    self.scenes = []
    self.scene_index = -1
    self.volume_inputs = []

    self.stream_state = OBS.OUTPUT_STOPPED # TODO: initialise these values on connect
    self.record_state = OBS.OUTPUT_STOPPED 

    self.on_scene_change = lambda x: None
    self.on_stream_change = lambda x: None
    self.on_record_change = lambda x: None

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
      self.update_volume_inputs()

      # register any callbacks
      self.register_on_scene_change(self.on_scene_change)
      self.register_on_stream_change(self.on_stream_change)
      self.register_on_record_change(self.on_record_change)

      if self.verbose: print('Connected')

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
    except:
      return -1

  # -------------------- OBS Audio methods --------------------

  def update_volume_inputs(self):
    '''
    @summary:   Get audio inputs (for output capture)
    @author:    Brandon

    @return:    all volume inputs from OBS
    @rtype:     list
    '''
    try:
      inputs = self.request.get_input_list().inputs
      self.volume_inputs = [volume for volume in inputs if volume['inputKind'] == 'wasapi_output_capture' or volume['inputKind'] == 'coreaudio_output_capture']
    except: pass
    return self.volume_inputs

  def get_volume(self, volume_input):
    '''
    @summary:   Get the volume of the provided input
    @author:    Brandon

    @param:     volume_input: the input to get the colume from
    @type:      Request

    @return:    volume of input in decibels
    @rtype:     float
    '''
    try: return self.request.get_input_volume(volume_input['inputName']).input_volume_db
    except: return -1

  def set_volume(self, input, name):
    '''
    @summary:   Set the volume of the provided input in decibels
    @author:    Brandon

    @param:     input: the volume to set the input to
    @type:      float

    @param:     name: the name of the input to change volume of
    @type:      string
    '''
    try:
      input = int(input)
      self.request.set_input_volume(name, vol_db=input)
      return input
    except: return -1

  # -------------------- OBS Stream/recording methods --------------------

  def toggle_stream(self):
    try: self.request.toggle_stream()
    except: pass


  def toggle_record(self):
    try: self.request.toggle_record()
    except: pass

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

    # also register the same callback on sceneListChanged 
    # however websockets does not support callback on scene reordering yet)
    def on_scene_list_changed(data):
      on_current_program_scene_changed(data)

    try:
      self.event.callback.register(on_current_program_scene_changed)
      self.event.callback.register(on_scene_list_changed)
    except: pass

  def register_on_stream_change(self, callback):
    '''
    Register a callback function on stream state change that takes output_state as a parameter
    @param callback eg. def callback(output_state): pass
    output_state is either OBS.OUTPUT_STARTED or OBS.OUTPUT_STOPPED
    '''

    # if disconnected, store callback to be registered on reconnect
    self.on_stream_change = callback

    def on_stream_state_changed(data):
      if data.output_state in ['OBS_WEBSOCKET_OUTPUT_STARTED', 'OBS_WEBSOCKET_OUTPUT_STOPPED']:
        self.stream_state = OBS.OUTPUT_STARTED if data.output_state == 'OBS_WEBSOCKET_OUTPUT_STARTED' else OBS.OUTPUT_STOPPED
        callback(self.stream_state)

    try: self.event.callback.register(on_stream_state_changed)
    except: pass
  
  def register_on_record_change(self, callback):
    '''
    Register a callback function on record state change that takes output_state as a parameter
    @param callback eg. def callback(output_state): pass
    output_state is either OBS.OUTPUT_STARTED or OBS.OUTPUT_STOPPED
    '''

    # if disconnected, store callback to be registered on reconnect
    self.on_record_change = callback

    def on_record_state_changed(data):
      if data.output_state in ['OBS_WEBSOCKET_OUTPUT_STARTED', 'OBS_WEBSOCKET_OUTPUT_STOPPED']:
        self.record_state = OBS.OUTPUT_STARTED if data.output_state == 'OBS_WEBSOCKET_OUTPUT_STARTED' else OBS.OUTPUT_STOPPED
        callback(self.record_state)

    try: self.event.callback.register(on_record_state_changed)
    except: pass

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
