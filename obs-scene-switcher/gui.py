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

leds = []

def on_current_program_scene_changed(data):
  scenes = get_scenes()
  for i in range(8):
    if i == [s['sceneIndex'] for s in scenes if s['sceneName'] == data.scene_name][0]: leds[i]['bg'] = 'red'
    else: leds[i]['bg'] = 'white'

def main():
  global leds

  event.callback.register(on_current_program_scene_changed)

  scenes = get_scenes()
  sceneName = request.get_current_program_scene().current_program_scene_name
  s = [s['sceneIndex'] for s in scenes if s['sceneName'] == sceneName][0]

  m = tk.Tk()
  # m.geometry('500x500')

  buttons = [tk.Button(m, text=i+1, command=lambda s=i: set_scene(s)) for i in range(8)]
  for i, b in enumerate(buttons): b.grid(column=0 if i<4 else 2, row=i%4)
  
  leds = [tk.Label(m, text=' ', bg='red' if i==s else 'white') for i in range(8)]
  for i, l in enumerate(leds): l.grid(column=1 if i<4 else 3, row=i%4)

  m.mainloop()

if __name__ == '__main__':
  main()