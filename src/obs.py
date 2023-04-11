'''Interface with OBS via websockets'''

import obsws_python as obs

class OBS():
  
  def __init__(self, host, port, password):
    self.request = None
    self.event = None
    self.connect(host, port, password)

  def connect(self, host, port, password):
    try:
      self.request = obs.ReqClient(host, port, password)
      self.event = obs.EventClient(host, port, password)
    except: pass

  def set_on_scene_change(self, callback):
    def on_current_program_scene_changed(data): callback(data)
    if self.event:
      self.event.callback.register(on_current_program_scene_changed)