'''
Interface with Microsoft PowerPoint via Applescript for Mac and COM32 for Windows
'''

import subprocess
import pathlib
import platform

os = platform.system()

#Variables for Mac:
PREVIOUS = 126 # key code
NEXT = 125
SCRIPT = pathlib.Path(__file__).parent / '../script/change_slide.applescript'

#Variables for Win:
if os == 'Windows':
  import win32com.client as win32
  

def change_slide(key):
  if os == 'Darwin': change_slide_apple(key)
  elif os == 'Windows': change_slide_windows(key)

def change_slide_apple(key):
  if key in [PREVIOUS, NEXT]:
    subprocess.run(f'osascript {SCRIPT} {key}', shell=True)

def change_slide_windows(key):
  app = win32.Dispatch('PowerPoint.Application')
  pres = app.ActivePresentation
  #if pres.SlideShowWindow.Active(): 
  if key == NEXT: pres.SlideShowWindow.View.Next()
  elif key == PREVIOUS: pres.SlideShowWindow.View.Previous()
  #else:
  #  print("Slideshow not active")

if __name__ == '__main__':
  while True:
    key = input().strip()
    if key in 'aw': change_slide(PREVIOUS)
    else: change_slide(NEXT)