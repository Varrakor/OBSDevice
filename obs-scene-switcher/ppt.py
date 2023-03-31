import os, curses

script = """tell application "Microsoft PowerPoint"
	# activate
	set theView to view of document window 1
	my {}(theView)
end tell

on goToNextSlide(theView)
	tell application "Microsoft PowerPoint"
		# activate
		set curSlide to slide index of slide range of selection of document window 1
		go to slide theView number (curSlide + 1)
	end tell
end goToNextSlide

on goToPreviousSlide(theView)
	tell application "Microsoft PowerPoint"
		# activate
		set curSlide to slide index of slide range of selection of document window 1
		go to slide theView number (curSlide - 1)
	end tell
end goToPreviousSlide"""

file = 'apple.SCPT'

# Initialize the terminal
win = curses.initscr()

# Turn off line buffering
curses.cbreak()

# Make getch() non-blocking
win.nodelay(True)

while True:
    try: key = chr(win.getch())
    except ValueError: continue
    try:
      if key in 'aw': lines = script.format('goToPreviousSlide').split('\n')
      elif key in 'ds': lines = script.format('goToNextSlide').split('\n')
      if key in 'wsad':
        cmd = 'osascript'
        for l in lines: cmd += f' -e \'{l}\''
        os.system(cmd)
    except: exit()