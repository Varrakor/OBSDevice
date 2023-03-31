import obsws_python as obs
from dotenv import dotenv_values
import tkinter as tk

# using different obs websocket library from https://github.com/aatikturk/obsws-python

env = dotenv_values()

request = obs.ReqClient(host=env['HOST'], port=env['PORT'], password=env['PASSWORD'])
event = obs.EventClient(host=env['HOST'], port=env['PORT'], password=env['PASSWORD'])

def get_scenes():
  scenes = request.get_scene_list().scenes
  for s in scenes: s['sceneIndex'] = len(scenes) - s['sceneIndex'] - 1
  return sorted(scenes, key=lambda s: s['sceneIndex'])

def set_scene(s):
  scenes = get_scenes()
  if s >= 0 and s < len(scenes):
    sceneName = scenes[s]['sceneName']
    print(f'Switching to {sceneName}')
    request.set_current_program_scene(sceneName)
    return s
  return -1

def get_volume_inputs():
  """
  @summary:   Get audio inputs (for output capture)
  @author:    Brandon

  @return:    all volume inputs from OBS
  @rtype:     list
  """
  inputs = request.get_input_list().inputs
  volume_inputs = [volume for volume in inputs if volume['inputKind'] == 'wasapi_output_capture']
  return volume_inputs

def get_volume(volume_input):
  """
  @summary:   Get the volume of the provided input
  @author:    Brandon

  @param:     volume_input: the input to get the colume from
  @type:      Request

  @return:    volume of input in decibels
  @rtype:     float
  """
  volume = request.get_input_volume(volume_input['inputName'])
  return volume.input_volume_db

def set_volume(input, name):
  """
  @summary:   Set the volume of the provided input in decibels
  @author:    Brandon

  @param:     input: the volume to set the input to
  @type:      float

  @param:     name: the name of the input to change volume of
  @type:      string
  """
  request.set_input_volume(name, vol_db=int(input))

leds = []
rec, stream = None, None

def on_current_program_scene_changed(data):
  scenes = get_scenes()
  for i in range(8):
    if i == [s['sceneIndex'] for s in scenes if s['sceneName'] == data.scene_name][0]: leds[i]['bg'] = 'blue'
    else: leds[i]['bg'] = 'white'

def on_stream_state_changed(data):
  if data.output_state == 'OBS_WEBSOCKET_OUTPUT_STARTED': stream['text'] = 'Stop Streaming'
  elif data.output_state == 'OBS_WEBSOCKET_OUTPUT_STOPPED': stream['text'] = 'Start Streaming'

def on_record_state_changed(data):
  if data.output_state == 'OBS_WEBSOCKET_OUTPUT_STARTED': rec['text'] = 'Stop Recording'
  elif data.output_state == 'OBS_WEBSOCKET_OUTPUT_STOPPED': rec['text'] = 'Start Recording'

def main():
  global leds, rec, stream

  event.callback.register(on_current_program_scene_changed)
  event.callback.register(on_record_state_changed)
  event.callback.register(on_stream_state_changed)

  scenes = get_scenes()
  volume_inputs = get_volume_inputs()
  sceneName = request.get_current_program_scene().current_program_scene_name
  s = [s['sceneIndex'] for s in scenes if s['sceneName'] == sceneName][0]

  m = tk.Tk()
  # m.geometry('500x500')

  buttons = [tk.Button(m, text=i+1, command=lambda s=i: set_scene(s)) for i in range(8)]
  for i, b in enumerate(buttons): b.grid(column=0 if i<4 else 2, row=i%4)
  
  leds = [tk.Label(m, text=' ', bg='blue' if i==s else 'white') for i in range(8)]
  for i, l in enumerate(leds): l.grid(column=1 if i<4 else 3, row=i%4)

  stream = tk.Button(m, text='Start Streaming', command=request.toggle_stream)
  stream.grid(column=4, row=0)
  rec = tk.Button(m, text='Start Recording', command=request.toggle_record)
  rec.grid(column=4, row=1)

  for i in range(len(volume_inputs)):
    audio = volume_inputs[i]
    current_volume = get_volume(audio)
    slider = tk.Scale(m, label=f'{audio["inputName"]}', orient='horizontal', from_=-100.0, to=0.0, length=150, command= lambda val, name=audio["inputName"]: set_volume(val, name))
    slider.set(current_volume)
    slider.grid(column=5, row=i)

  m.mainloop()

if __name__ == '__main__':
  main()