import tkinter as tk
import device
import os
import json
import obs
import threading

# persistent settings storage
file = os.path.expanduser('~/.OBSDevice.json')

# GUI sizing
GEOMETRY = '400x300'
COL0 = 120
COL1 = 250
MASTER_PADDING = 10

# serial port options menu default
EMPTY_PORT_MSG = 'No port detected'

class App():
	def __init__(self, verbose=False):
		
		try:
			# get previous settings
			with open(file, 'r') as f:
				data = json.load(f)

		except:
			# make new settings file
			with open(file, 'w') as f:
				data = {'obs_port': obs.DEFAULT_PORT, 'obs_password': ''}
				json.dump(data, f)

		self.interface = device.DeviceInterface(
			obs_port=data['obs_port'],
			obs_password=data['obs_password'],
			verbose=verbose
		)

		# loop device interface in new thread
		threading.Thread(daemon=True, target=self.interface.loop).start()

		self.master = tk.Tk()
		self.master.geometry(GEOMETRY)
		self.master.title('OBSDevice')

		master_frame = tk.Frame(self.master)
		master_frame.grid(row=0, column=0, padx=MASTER_PADDING, pady=MASTER_PADDING)

		# Connect lights

		light_frame = tk.LabelFrame(master_frame, text='Connection')
		light_frame.grid(row=0, column=0)
		light_frame.columnconfigure(0, minsize=COL0)
		light_frame.columnconfigure(1, minsize=COL1)

		label = tk.Label(light_frame, text='OBS connection')
		label.grid(row=0, column=0, sticky='E', padx=5, pady=5)

		d = 20
		self.obs_canvas = tk.Canvas(light_frame, width=d, height=d)
		self.obs_light = self.obs_canvas.create_oval(5, 5, d, d, fill=('green' if self.interface.obs.connected else 'red'), outline='')
		self.obs_canvas.grid(row=0, column=1, sticky='W', padx=5, pady=5)

		def on_obs_connect():
			self.obs_canvas.itemconfig(self.obs_light, fill='green')

		def on_obs_disconnect():
			self.obs_canvas.itemconfig(self.obs_light, fill='red')

		self.interface.obs.connect_callback = on_obs_connect
		self.interface.obs.disconnect_callback = on_obs_disconnect

		label = tk.Label(light_frame, text='Serial connection')
		label.grid(row=1, column=0, sticky='E', padx=5, pady=5)

		self.serial_canvas = tk.Canvas(light_frame, width=d, height=d)
		self.serial_light = self.serial_canvas.create_oval(5, 5, d, d, fill=('green' if self.interface.connected else 'red'), outline='')
		self.serial_canvas.grid(row=1, column=1, sticky='W', padx=5, pady=5)

		# OBS port number

		obs_frame = tk.LabelFrame(master_frame, text='OBS')
		obs_frame.grid(row=1, column=0)
		obs_frame.columnconfigure(0, minsize=COL0)
		obs_frame.columnconfigure(1, minsize=COL1)

		label = tk.Label(obs_frame, text="OBS port number")
		label.grid(row=0, column=0, sticky='E', padx=5, pady=5)

		self.obs_port_text = tk.StringVar()
		self.obs_port_text.set(self.interface.obs.port)

		def set_port(*_):
			try:
				self.interface.obs.port = int(self.obs_port_text.get())
				
				with open(file, 'r') as f:
					data = json.load(f)
					data['obs_port'] = self.interface.obs.port

				with open(file, 'w') as f:
					json.dump(data, f)

			except: pass

		self.obs_port_text.trace_add("write", set_port)

		obs_port_entry = tk.Entry(obs_frame, textvariable=self.obs_port_text)
		obs_port_entry.grid(row=0, column=1, sticky='W', padx=5, pady=5)

		# OBS password

		label = tk.Label(obs_frame, text="OBS password")
		label.grid(row=1, column=0, sticky='E', padx=5, pady=5)

		self.obs_password_text = tk.StringVar()
		self.obs_password_text.set(self.interface.obs.password)

		def set_password(*_):
			self.interface.obs.password = self.obs_password_text.get()

			with open(file, 'r') as f:
				data = json.load(f)
				data['obs_password'] = self.interface.obs.password

			with open(file, 'w') as f:
				json.dump(data, f)

		self.obs_password_text.trace_add("write", set_password)

		obs_password_entry = tk.Entry(obs_frame, textvariable=self.obs_password_text)
		obs_password_entry.grid(row=1, column=1, sticky='W', padx=5, pady=5)

		# Serial ports

		serial_frame = tk.LabelFrame(master_frame, text='Device')
		serial_frame.grid(row=2, column=0)
		serial_frame.columnconfigure(0, minsize=COL0)
		serial_frame.columnconfigure(1, minsize=COL1)

		label = tk.Label(serial_frame, text='Select port')
		label.grid(row=0, column=0, sticky='E', padx=5, pady=5)

		self.serial_port_text = tk.StringVar(self.master)
		self.serial_port_text.set(self.interface.serial_port or EMPTY_PORT_MSG)

		def on_serial_connect():
			self.serial_port_text.set(self.interface.serial_port or EMPTY_PORT_MSG)
			self.serial_canvas.itemconfig(self.serial_light, fill='green')

		def on_serial_disconnect():
			self.serial_canvas.itemconfig(self.serial_light, fill='red')

		self.interface.connect_callback = on_serial_connect
		self.interface.disconnect_callback = on_serial_disconnect

		def set_serial_port(*_):
			if self.serial_port_text.get() != EMPTY_PORT_MSG:
				self.interface.serial_port = self.serial_port_text.get()

		self.serial_port_text.trace_add("write", set_serial_port)

		port_names = [p.device for p in self.interface.get_ports()] or [EMPTY_PORT_MSG]
		self.port_list = tk.OptionMenu(serial_frame, self.serial_port_text, *port_names)
		self.port_list.config(width=16)
		self.port_list.grid(row=0, column=1, sticky='W', padx=5, pady=5)

		def refresh_ports():
			self.serial_port_text.set(self.interface.serial_port or EMPTY_PORT_MSG)
			self.port_list['menu'].delete(0, 'end')
			new_choices = [p.device for p in self.interface.serial_ports] or [EMPTY_PORT_MSG]
			for choice in new_choices:
				self.port_list['menu'].add_command(label=choice, command=tk._setit(self.serial_port_text, choice))

		button = tk.Button(serial_frame, command=refresh_ports, text='Refresh')
		button.grid(row=1, column=1, sticky='W', padx=5, pady=5)

	def loop(self):
		self.master.mainloop()

App().loop()