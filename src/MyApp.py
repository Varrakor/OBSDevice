'''The MacOS Application'''

if __name__ == '__main__':
  from gui import GUI
  from dotenv import dotenv_values

  env = dotenv_values('../.env')
  GUI(env['PASSWORD'], env['HOST'], env['PORT']).loop()