import tkinter as tk

from dotenv import dotenv_values
from gui import GUI


class ConfigureApp():
    def __init__(self):
        # Base set up of configuration app that will connect to the GUI
        self.master = tk.Tk()
        env = dotenv_values()

        # Set up attribute for App to store a GUI object
        self.gui = ''

        # Set up password field for configuration app
        if 'OBS_PASSWORD' in env.keys():
            def_password = env['OBS_PASSWORD']
        else:
            def_password = 'password'
        
        self.passwordLabel = tk.Label(self.master, text="OBS Password:", width=20)
        self.passwordLabel.grid(column=0, row=0)
        self.password = tk.Entry(self.master, width=30)
        self.password.insert(0, def_password)
        self.password.grid(column=1, row=0, padx=10, pady=10)

        # Set up host field for configuration app
        if 'HOST' in env.keys():
            def_host = env['HOST']
        else:
            def_host = 'localhost'
        
        self.hostLabel = tk.Label(self.master, text="Host:", width=20)
        self.hostLabel.grid(column=0, row=1)
        self.host = tk.Entry(self.master, width=30)
        self.host.insert(0, def_host)
        self.host.grid(column=1, row=1, padx=10, pady=10)

        # Set up port field for configuration app
        if 'PORT' in env.keys():
            def_port = env['PORT']
        else:
            def_port = '4455'
        
        self.portLabel = tk.Label(self.master, text="Port:", width=20)
        self.portLabel.grid(column=0, row=2)
        self.port = tk.Entry(self.master, width=30)
        self.port.insert(0, def_port)
        self.port.grid(column=1, row=2, padx=10, pady=5)

        # Set up button that will start the GUI with the provided setting on the configuration app
        self.appButton = tk.Button(self.master, text='Start App', command=self.start_app)
        self.appButton.grid(column=0, row=4, padx=10, pady=20)

    
    def start_app(self):
        """
        @summary:   Start the GUI of the video switcher. If the GUI is not currently running, enable it. Otherwise, disable it to avoid duplicating GUIs.
        @author:    Brandon
        """
        # These lines may not be necessary when not testing with GUI
        self.master.quit()

    def loop(self):
        self.master.mainloop()


def process():
    """
    @summary:   Function to continuously run Configuration App to set up GUI for OBS Video Switcher
    @author:    Brandon
    """
    while True:
        app = ConfigureApp()
        app.loop()

        try:
            password = app.password.get()
            port = app.port.get()
            host = app.host.get()

            params = [password, port, host]
            
            if any(not param for param in params):
                print('NOT ENOUGH PARAMETERS WERE PROVIDED TO CONNECT TO THE OBS! TRY AGAIN...')
                app.master.destroy()
                continue
            
            gui = GUI(password, port=port, host=host)
            app.master.destroy()
            gui.loop()
        except:
            # If the Configuration App was closed by the user, close entier process
            break


if __name__ == '__main__':
    process()