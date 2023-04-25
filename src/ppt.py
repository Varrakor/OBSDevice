'''Interface with Microsoft PowerPoint via Applescript for Mac and COM32 for Windows'''
import win32com.client as win32
import subprocess
import pathlib
import platform

#Variables for Mac:
PREVIOUS = 126 # key code
NEXT = 125
SCRIPT = pathlib.Path(__file__).parent / '../script/change_slide.applescript'

#Variables for Win:
app = win32.Dispatch("PowerPoint.Application")
ppt = app.ActivePresentation

def change_slide(key):
  os = platform.system()
  if (os == "Windows"):
    change_slide_windows(key)
  elif (os == "Darwin"):
    change_slide_apple(key)

def change_slide_apple(key):
  if key in [PREVIOUS, NEXT]:
    subprocess.run(f'osascript {SCRIPT} {key}', shell=True)

def change_slide_windows(key):
  if (key == NEXT):
    ppt.SlideShowWindow.View.Next()
  elif (key == PREVIOUS):
    ppt.SlideShowWindow.View.Previous()

if __name__ == '__main__':
  while True:
    key = input().strip()
    if key in 'aw': change_slide(PREVIOUS)
    else: change_slide(NEXT)