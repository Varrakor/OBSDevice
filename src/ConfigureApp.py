import tkinter as tk

from dotenv import dotenv_values
from gui import GUI


class ConfigureApp():
    def __init__(self):
        # Base set up of configuration app that will connect to the GUI
        self.master = tk.Tk()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing_app)
        env = dotenv_values()

        # Set up attribute for App to store a GUI object
        self.gui = ''

        # Set up password field for configuration app
        def_password = env['OBS_PASSWORD']
        self.passwordLabel = tk.Label(self.master, text="OBS Password:", width=20)
        self.passwordLabel.grid(column=0, row=0)
        self.password = tk.Entry(self.master, width=30)
        self.password.insert(0, def_password)
        self.password.grid(column=1, row=0, padx=10, pady=10)

        # Set up host field for configuration app
        def_host = env['HOST']
        self.hostLabel = tk.Label(self.master, text="Host:", width=20)
        self.hostLabel.grid(column=0, row=1)
        self.host = tk.Entry(self.master, width=30)
        self.host.insert(0, def_host)
        self.host.grid(column=1, row=1, padx=10, pady=10)

        # Set up port field for configuration app
        def_port = env['PORT']
        self.portLabel = tk.Label(self.master, text="Port:", width=20)
        self.portLabel.grid(column=0, row=2)
        self.port = tk.Entry(self.master, width=30)
        self.port.insert(0, def_port)
        self.port.grid(column=1, row=2, padx=10, pady=5)

        # Set up button that will start the GUI with the provided setting on the configuration app
        self.appButton = tk.Button(self.master, text='Start App', command=self.start_app)
        self.appButton.grid(column=0, row=4, padx=10, pady=20)

        # Set up button that will stop the currently running GUI
        self.stopButton = tk.Button(self.master, text='Stop App', command=self.stop_app)
        self.stopButton.config(state = tk.DISABLED)
        self.stopButton.grid(column=1, row=4, padx=10, pady=20)
    
    def start_app(self):
        """
        @summary:   Start the GUI of the video switcher. If the GUI is not currently running, enable it. Otherwise, disable it to avoid duplicating GUIs.
        @author:    Brandon
        """
        # These lines may not be necessary when not testing with GUI
        self.appButton.config(state = tk.DISABLED)
        self.stopButton.config(state = tk.NORMAL)
        self.gui = GUI(self.password.get(), port=self.port.get(), host=self.host.get())
        self.gui.master.protocol("WM_DELETE_WINDOW", self.on_closing_gui)
    
    def stop_app(self):
        """
        @summary:   Stop the app of the video switcher. If the GUI is not currently running, disable it. Otherwise, have it enabled.
        @author:    Brandon
        """
        self.appButton.config(state = tk.NORMAL)
        self.stopButton.config(state = tk.DISABLED)
        self.gui.force_close()
        self.gui = ''

    
    def on_closing_gui(self):
        """
        @summary:   If the termination (close window) of the GUI is detected, enable the button on the ConfigureApp that will start the GUI, and disable the stop button.
        @author:    Brandon
        """
        self.gui.force_close()
        self.gui = ''
        if self.appButton["state"] == tk.DISABLED:
            self.appButton.config(state = tk.NORMAL)
        if self.stopButton["state"] == tk.NORMAL:
            self.stopButton.config(state = tk.DISABLED)
    
    def on_closing_app(self):
        """
        @summary:   When ConfigureApp itself closes, also close the GUI connected to it.
        @author:    Brandon
        """
        if self.gui:
            self.gui.force_close()
        self.master.destroy()

    def loop(self):
        self.master.mainloop()


if __name__ == '__main__':
    ConfigureApp().loop()