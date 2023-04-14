'''The MacOS Application'''

if __name__ == '__main__':
  from gui import GUI
  from dotenv import dotenv_values

  env = dotenv_values()
  
  GUI(env['OBS_PASSWORD']).loop()