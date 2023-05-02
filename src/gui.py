import tkinter as tk
from obs import OBS
import ppt

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
    self.stream_button = tk.Button(self.master, text='Stop Streaming' if self.obs.is_streaming else 'Start Streaming', command=self.obs.toggle_stream)
    self.stream_button.grid(column=4, row=0)

    self.rec_button = tk.Button(self.master, text='Stop Recording' if self.obs.is_recording else 'Start Recording', command=self.obs.toggle_record)
    self.rec_button.grid(column=4, row=1)

    # powerpoint buttons
    self.prev_button = tk.Button(self.master, text='Previous', command=lambda: ppt.previous_slide())
    self.prev_button.grid(column=0, row=4)

    self.next_button = tk.Button(self.master, text='Next', command=lambda: ppt.next_slide())
    self.next_button.grid(column=1, row=4)


    # audio slider (only for mic)
    slider = tk.Scale(self.master, label=f"{self.obs.mic_name}", orient='horizontal', from_=-100.0, to=0.0, length=150, command=lambda vol_db: self.obs.set_volume(vol_db))
    slider.set(self.obs.volume)
    slider.grid(column=5, row=0)
    
    self.mute_button = tk.Button(self.master, text='Unmute' if self.obs.is_muted else 'Mute', command=self.obs.toggle_mute)
    self.mute_button.grid(column=5, row=2)

    # register OBS callbacks
    self.obs.register_on_scene_change(lambda scene_index: self.on_scene_change(scene_index))
    self.obs.register_on_stream_change(lambda is_streaming: self.on_stream_change(is_streaming))
    self.obs.register_on_record_change(lambda is_recording: self.on_record_change(is_recording))
    self.obs.register_on_mute_change(lambda is_muted: self.on_mute_change(is_muted))

  def on_scene_change(self, scene_index):
    for i in range(8):
      if i == scene_index: self.leds[i]['bg'] = 'red'
      else: self.leds[i]['bg'] = 'white'

  def on_stream_change(self, is_streaming):
    if is_streaming: self.stream_button['text'] = 'Stop Streaming'
    else: self.stream_button['text'] = 'Start Streaming'

  def on_record_change(self, is_recording):
    if is_recording: self.rec_button['text'] = 'Stop Recording'
    else: self.rec_button['text'] = 'Start Recording'
  
  def on_mute_change(self, is_muted):
    if is_muted: self.mute_button['text'] = 'Unmute'
    else: self.mute_button['text'] = 'Mute'
  
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