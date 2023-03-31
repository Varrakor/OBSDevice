import subprocess

UP=126
DOWN=125

script="""tell application "Microsoft PowerPoint"
  activate
  tell app "System Events" to key code {}
end tell"""

while True:
  key = input()
  if key in 'aw': lines = script.format(UP).split('\n')
  elif key in 'ds': lines = script.format(DOWN).split('\n')
  if key in 'wsad':
    cmd = 'osascript'
    for l in lines: cmd += f' -e \'{l}\''
    subprocess.run(cmd, shell=True)