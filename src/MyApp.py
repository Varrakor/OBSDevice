'''The MacOS Application'''

if __name__ == '__main__':
  from gui import GUI
  from dotenv import dotenv_values

  env = dotenv_values('../.env')
  GUI(env['OBS_PASSWORD'], env['OBS_HOST'], env['OBS_PORT']).loop()