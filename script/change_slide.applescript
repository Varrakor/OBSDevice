# Run script with one command-line argument: either 126 (previous) or 125 (next)

# Currently does not handle minimised or closed windows
# PowerPoint will activate, unactivating the current app, but nothing else will happen

property app_name : "Microsoft PowerPoint"

on run argv

if application app_name is running
  tell application app_name
    activate
    tell application "System Events" to key code (item 1 of argv)
  end tell
end if

end run