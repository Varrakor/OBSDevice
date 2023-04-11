'''Interface with Microsoft PowerPoint via Applescript'''

import subprocess
import pathlib

class PPT():

  PREVIOUS = 126
  NEXT = 125

  SCRIPT = pathlib.Path(__file__).parent / '../script/change_slide.applescript'

  @classmethod
  def change_slide(key):
    if key in [PPT.PREVIOUS, PPT.NEXT]:
      subprocess.run(f'osascript {PPT.SCRIPT} {key}', shell=True)

if __name__ == '__main__':
  while True:
    key = input().strip()
    if key in 'aw': PPT.change_slide(PPT.PREVIOUS)
    else: PPT.change_slide(PPT.NEXT)