'''
Interface with Microsoft PowerPoint via Applescript for Mac and COM32 for Windows
'''

import subprocess
import pathlib
import platform

os = platform.system()

# Mac
PREVIOUS = 126 # key code
NEXT = 125
SCRIPT = pathlib.Path(__file__).parent / '../script/change_slide.applescript'

# Windows
if os == 'Windows':
  import win32com.client as win32
  
def previous_slide():
  if os == 'Darwin': change_slide_apple(PREVIOUS)
  elif os == 'Windows': change_slide_windows(PREVIOUS)

def next_slide():
  if os == 'Darwin': change_slide_apple(NEXT)
  elif os == 'Windows': change_slide_windows(NEXT)

def change_slide_apple(key):
  if key in [PREVIOUS, NEXT]:
    subprocess.run(f'osascript {SCRIPT} {key}', shell=True)

def change_slide_windows(key):
  app = win32.Dispatch('PowerPoint.Application')
  try:
    pres = app.ActivePresentation
  except:
    print("No presentation is open")
    return

  slideshow = app.SlideShowWindows.Count # Number of active slideshows
  if (slideshow == 1): # 1 Slideshow open, act as expected
    if key == NEXT: pres.SlideShowWindow.View.Next()
    elif key == PREVIOUS: pres.SlideShowWindow.View.Previous()
  elif (slideshow > 1): # Multiple slideshows open, don't do anything
    print("Multiple Slideshows are open")
  elif (slideshow == 0): # No slideshows open, use document
    if (app.Windows.Count == 1): # One document open, act as usual
      window = app.Windows(1).View
      currentSlide = window.Slide.SlideNumber
      numberOfSlides = pres.Slides.Count
      if key == NEXT: window.GoToSlide(min(currentSlide + 1, numberOfSlides))
      elif key == PREVIOUS: window.GoToSlide(max(currentSlide - 1, 1))
    else: # Multiple documents open, don't
      print("Multiple powerpoints open, only use one")

if __name__ == '__main__':
  while True:
    key = input().strip()
    if key in 'aw': previous_slide()
    else: next_slide(NEXT)