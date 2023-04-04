import subprocess

UP=126
DOWN=125

# simple arrow presses
script='''tell application "Microsoft PowerPoint"
  activate
  tell app "System Events" to key code {}
end tell'''

def ppt(key):
  if key == 'prev': lines = script.format(UP).split('\n')
  elif key == 'next': lines = script.format(DOWN).split('\n')
  if key in 'prevnext':
    cmd = 'osascript'
    for l in lines: cmd += f' -e \'{l}\''
    subprocess.run(cmd, shell=True)

if __name__ == '__main__':
  while True:
    key = input().strip()
    if key in 'wa': ppt('prev')
    else: ppt('next')