import subprocess
import pathlib

PPT_PREVIOUS = 126
PPT_NEXT = 125

SCRIPT = pathlib.Path(__file__).parent / '../script/change_slide.applescript'

def change_slide(key):
  if key in [PPT_PREVIOUS, PPT_NEXT]:
    subprocess.run(f'osascript {SCRIPT} {key}', shell=True)

if __name__ == '__main__':
  while True:
    key = input().strip()
    if key in 'wa': change_slide(PPT_PREVIOUS)
    else: change_slide(PPT_NEXT)