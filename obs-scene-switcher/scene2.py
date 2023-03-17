import obsws_python as obs
from dotenv import dotenv_values

env = dotenv_values()

class Client():
  def __init__(self):
    self.request = obs.ReqClient(host=env['HOST'], port=env['PORT'], password=env['PASSWORD'])
    self.event = obs.EventClient(host=env['HOST'], port=env['PORT'], password=env['PASSWORD'])

client = Client()

def on_current_program_scene_changed(data):
  print(f'Switched to {data.scene_name}')
  scenes = client.request.get_scene_list().scenes
  # send Serial

def main():
  client.event.callback.register(on_current_program_scene_changed)

  scenes = client.request.get_scene_list().scenes
  print(scenes)

  while True:
    pass
    # listen for button press

if __name__ == '__main__':
  main()