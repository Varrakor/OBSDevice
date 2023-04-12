'''Interface with Microsoft PowerPoint via Applescript'''

import subprocess
import pathlib

PREVIOUS = 126 # key code
NEXT = 125

SCRIPT = pathlib.Path(__file__).parent / '../script/change_slide.applescript'

def change_slide(key):
  if key in [PREVIOUS, NEXT]:
    subprocess.run(f'osascript {SCRIPT} {key}', shell=True)

if __name__ == '__main__':
  while True:
    key = input().strip()
    if key in 'aw': change_slide(PREVIOUS)
    else: change_slide(NEXT)