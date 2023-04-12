'''
Interface with OBS via websockets

If disconnected to OBS, tries to reconnect whenever a method is called, otherwise does nothing
'''

import obsws_python

class OBS():
  
  def __init__(self, password, host='localhost', port=4455, verbose=False):
    '''
    @param password OBS websocket password set in OBS app settings
    '''
    self.host = host
    self.port = port
    self.password = password
    self.verbose = verbose
    
    self.request = None
    self.event = None
    
    self.scenes = []
    self.volume_inputs = []
    self.volume = 0

    self.on_scene_change = lambda x: None
    self.on_stream_change = lambda x: None
    self.on_record_change = lambda x: None

    self.connect()

    if self.connected():
      self.update_scenes()
      self.update_volume_inputs()

  def connected(self):
    return self.request and self.event

  def connect(self):
    '''
    Connect to OBS websocket
    Register any callbacks that have already been attempted to be registered
    '''
    try:
      self.request = obsws_python.ReqClient(host=self.host, port=self.port, password=self.password)
      self.event = obsws_python.EventClient(host=self.host, port=self.port, password=self.password)

      # register any callbacks
      self.register_on_scene_change(self.on_scene_change)
      self.register_on_stream_change(self.on_stream_change)
      self.register_on_record_change(self.on_record_change)

    except:
      self.request, self.event = None, None
      if self.verbose: print('Could not connect to OBS')

  def update_scenes(self):
    '''
    Store latest scene list
    Reverse scene indices so that index 0 is the top of the list
    '''
    if not self.connected(): self.connect()
    if not self.connected(): return

    scenes = self.request.get_scene_list().scenes
    for s in scenes: s['sceneIndex'] = len(scenes) - s['sceneIndex'] - 1 # scene indices reversed
    self.scenes = sorted(scenes, key=lambda s: s['sceneIndex'])
  
  def get_scene_index(self, sceneName):
    '''
    @return scene index for a given sceneName in the current scene list else -1 if not found
    '''
    for s in self.scenes:
      if s['sceneName'] == sceneName: return s['sceneIndex']
    return -1
  
  def get_current_scene(self):
    '''
    Updates scene list and returns current sceneIndex
    '''
    if not self.connected(): self.connect()
    if not self.connected(): return

    self.update_scenes()
    sceneName = self.request.get_current_program_scene().current_program_scene_name

    for s in self.scenes:
      if s['sceneName'] == sceneName: return s['sceneIndex']
    return -1
  
  def set_scene(self, sceneIndex):
    '''
    Request OBS change scene to sceneIndex
    Firstly, update scene list
    @return sceneIndex if successful else -1
    '''
    if not self.connected(): self.connect()
    if not self.connected(): return

    self.update_scenes()
    if sceneIndex >= 0 and sceneIndex < len(self.scenes):
      sceneName = self.scenes[sceneIndex]['sceneName']
      self.request.set_current_program_scene(sceneName)
      if self.verbose: print(f'Switched to {sceneName}')
      return sceneIndex
    return -1

  def register_on_scene_change(self, callback):
    '''
    Register a callback function on scene change that takes current sceneIndex as parameter
    Updates scene list before callback
    @param callback eg. def callback(sceneIndex): pass
    '''

    # if disconnected, store callback to be registered on reconnect
    self.on_scene_change = callback

    if not self.connected(): self.connect()
    if not self.connected(): return
  
    def on_current_program_scene_changed(data):
      self.update_scenes()
      callback(self.get_scene_index(data.scene_name)) # callback takes sceneIndex as parameter

    self.event.callback.register(on_current_program_scene_changed)

  # class variables
  OUTPUT_STARTED = True
  OUTPUT_STOPPED = False

  def register_on_stream_change(self, callback):
    '''
    Register a callback function on stream state change that takes output_state as a parameter
    @param callback eg. def callback(output_state): pass
    output_state is either OBS.OUTPUT_STARTED or OBS.OUTPUT_STOPPED
    '''

    # if disconnected, store callback to be registered on reconnect
    self.on_stream_change = callback

    if not self.connected(): self.connect()
    if not self.connected(): return

    def on_stream_state_changed(data):
      if data.output_state in ['OBS_WEBSOCKET_OUTPUT_STARTED', 'OBS_WEBSOCKET_OUTPUT_STOPPED']:
        callback(OBS.OUTPUT_STARTED if data.output_state == 'OBS_WEBSOCKET_OUTPUT_STARTED' else OBS.OUTPUT_STOPPED)

    self.event.callback.register(on_stream_state_changed)
  
  def register_on_record_change(self, callback):
    '''
    Register a callback function on record state change that takes output_state as a parameter
    @param callback eg. def callback(output_state): pass
    output_state is either OBS.OUTPUT_STARTED or OBS.OUTPUT_STOPPED
    '''

    # if disconnected, store callback to be registered on reconnect
    self.on_record_change = callback

    if not self.connected(): self.connect()
    if not self.connected(): return

    def on_record_state_changed(data):
      if data.output_state in ['OBS_WEBSOCKET_OUTPUT_STARTED', 'OBS_WEBSOCKET_OUTPUT_STOPPED']:
        callback(OBS.OUTPUT_STARTED if data.output_state == 'OBS_WEBSOCKET_OUTPUT_STARTED' else OBS.OUTPUT_STOPPED)

    self.event.callback.register(on_record_state_changed)

  def toggle_stream(self):
    if not self.connected(): self.connect()
    if not self.connected(): return

    self.request.toggle_stream()

  def toggle_record(self):
    if not self.connected(): self.connect()
    if not self.connected(): return

    self.request.toggle_record()

  def update_volume_inputs(self):
    '''
    @summary:   Get audio inputs (for output capture)
    @author:    Brandon

    @return:    all volume inputs from OBS
    @rtype:     list
    '''
    if not self.connected(): self.connect()
    if not self.connected(): return

    inputs = self.request.get_input_list().inputs
    self.volume_inputs = [volume for volume in inputs if volume['inputKind'] == 'wasapi_output_capture']

  def get_volume(self, volume_input):
    '''
    @summary:   Get the volume of the provided input
    @author:    Brandon

    @param:     volume_input: the input to get the colume from
    @type:      Request

    @return:    volume of input in decibels
    @rtype:     float
    '''
    if not self.connected(): self.connect()
    if not self.connected(): return

    volume = self.request.get_input_volume(volume_input['inputName'])
    return volume.input_volume_db

  def set_volume(self, input, name):
    '''
    @summary:   Set the volume of the provided input in decibels
    @author:    Brandon

    @param:     input: the volume to set the input to
    @type:      float

    @param:     name: the name of the input to change volume of
    @type:      string
    '''
    if not self.connected(): self.connect()
    if not self.connected(): return

    self.request.set_input_volume(name, vol_db=int(input))