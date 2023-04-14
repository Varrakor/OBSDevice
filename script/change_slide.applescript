property appName : "Microsoft PowerPoint"

# return true if app is running
on is_running(appName)
  tell application "System Events" to (name of processes) contains appName
end is_running

# return number of windows open of app
on window_is_open(appName)
  if my is_running(appName)
    tell application "System Events"
      tell process appName
        return count of windows > 0
      end tell
    end tell
  else 
    return 0
  end if
end window_is_open

on run argv

# send keym code from command-line to app
if my is_running(appName) and window_is_open(appName)
  tell application appName
    activate
    tell app "System Events" to key code (item 1 of argv)
  end tell
end if

end run