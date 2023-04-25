import tkinter as tk
from obs import OBS
import ppt
import ppt_windows
import platform

class GUI():
  
  def __init__(self, password, host='localhost', port=4455):
    self.obs = OBS(password, host, port)
    self.master = tk.Tk()

    # scene buttons and LEDs
    self.buttons = [tk.Button(self.master, text=i+1, command=lambda scene_index=i: self.obs.set_scene(scene_index)) for i in range(8)]
    for i, b in enumerate(self.buttons): b.grid(column=0 if i<4 else 2, row=i%4)
    
    self.leds = [tk.Label(self.master, text=' ', bg='red' if i==self.obs.scene_index else 'white') for i in range(8)]
    for i, l in enumerate(self.leds): l.grid(column=1 if i<4 else 3, row=i%4)

    # stream and recording buttons
    self.stream_button = tk.Button(self.master, text='Start Streaming' if self.obs.stream_state == OBS.OUTPUT_STOPPED else 'Stop Streaming', command=self.obs.toggle_stream)
    self.stream_button.grid(column=4, row=0)

    self.rec_button = tk.Button(self.master, text='Start Recording' if self.obs.record_state == OBS.OUTPUT_STOPPED else 'Stop Recording', command=self.obs.toggle_record)
    self.rec_button.grid(column=4, row=1)

    # powerpoint buttons
    self.prev_button = tk.Button(self.master, text='Previous', command=lambda: ppt.change_slide(ppt.PREVIOUS))
    self.prev_button.grid(column=0, row=4)

    self.next_button = tk.Button(self.master, text='Next', command=lambda: ppt.change_slide(ppt.NEXT))
    self.next_button.grid(column=1, row=4)

    # audio slider
    for i in range(len(self.obs.volume_inputs)):
      audio = self.obs.volume_inputs[i]
      current_volume = self.obs.get_volume(audio)
      slider = tk.Scale(self.master, label=f"{audio['inputName']}", orient='horizontal', from_=-100.0, to=0.0, length=150, command= lambda val, name=audio['inputName']: self.obs.set_volume(val, name))
      slider.set(current_volume)
      slider.grid(column=5, row=i)

    # register OBS callbacks
    self.obs.register_on_scene_change(lambda scene_index: self.on_scene_change(scene_index))
    self.obs.register_on_stream_change(lambda output_state: self.on_stream_change(output_state))
    self.obs.register_on_record_change(lambda output_state: self.on_record_change(output_state))

  def on_scene_change(self, scene_index):
    for i in range(8):
      if i == scene_index: self.leds[i]['bg'] = 'red'
      else: self.leds[i]['bg'] = 'white'

  def on_stream_change(self, output_state):
    if output_state == OBS.OUTPUT_STARTED: self.stream_button['text'] = 'Stop Streaming'
    elif output_state == OBS.OUTPUT_STOPPED: self.stream_button['text'] = 'Start Streaming'

  def on_record_change(self, output_state):
    if output_state == OBS.OUTPUT_STARTED: self.rec_button['text'] = 'Stop Recording'
    elif output_state == OBS.OUTPUT_STOPPED: self.rec_button['text'] = 'Start Recording'
  
  def force_close(self):
    """
    @summary:   Force stop the GUI by destroying it.
    @author:    Brandon
    """
    self.master.destroy()

  def loop(self):
    self.master.mainloop()


def main():
  from dotenv import dotenv_values
  env = dotenv_values()
  GUI(env['OBS_PASSWORD']).loop()

if __name__ == '__main__':
  main()