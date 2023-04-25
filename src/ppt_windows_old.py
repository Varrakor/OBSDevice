'''Interface with Microsoft PowerPoint for Windows'''
import win32com.client as win32

app = win32.Dispatch("PowerPoint.Application")
ppt = app.ActivePresentation

def next_slide():
    ppt.SlideShowWindow.View.Next()

def prev_slide():
    ppt.SlideShowWindow.View.Previous()

if __name__ == '__main__':
  while True:
    key = input().strip()
    if (key == "NEXT"):
        next_slide()
    elif (key == "PREVIOUS"):
        prev_slide()
