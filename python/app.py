import tkinter as tk
import device
import pathlib
import json
import obs

path = pathlib.Path(__file__).parent
file = path / 'data.json'

class App():
	def __init__(self, verbose=False):
		
		try:
			with open(file, 'r') as f:
				data = json.load(f)

		except:
			with open(file, 'w') as f:
				data = {'obs_port': obs.DEFAULT_PORT, 'obs_password': ''}
				json.dump(data)

		self.interface = device.DeviceInterface(
			obs_port=data['obs_port'],
			obs_password=data['obs_password'],
			verbose=verbose
		)

		self.master = tk.Tk()
		self.master.geometry('400x200')
		self.master.after(0, self.interface.poll)

		# Connect lights

		label = tk.Label(self.master, text='OBS connection')
		label.grid(row=0, column=0)

		d = 20
		self.obs_canvas = tk.Canvas(self.master, width=d, height=d)
		self.obs_light = self.obs_canvas.create_oval(5, 5, d, d, fill='red', outline='')
		self.obs_canvas.grid(row=0, column=1)

		def on_obs_connect():
			self.obs_canvas.itemconfig(self.obs_light, fill='green')

		def on_obs_disconnect():
			self.obs_canvas.itemconfig(self.obs_light, fill='red')

		self.interface.obs.connect_callback = on_obs_connect
		self.interface.obs.disconnect_callback = on_obs_disconnect

		label = tk.Label(self.master, text='Serial connection')
		label.grid(row=1, column=0)

		self.serial_canvas = tk.Canvas(self.master, width=d, height=d)
		self.serial_light = self.serial_canvas.create_oval(5, 5, d, d, fill='red', outline='')
		self.serial_canvas.grid(row=1, column=1)

		# OBS port number

		label = tk.Label(self.master, text="OBS port number")
		label.grid(row=2, column=0)

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

		obs_port_entry = tk.Entry(self.master, textvariable=self.obs_port_text)
		obs_port_entry.grid(row=2, column=1)

		# OBS password

		label = tk.Label(self.master, text="OBS password")
		label.grid(row=3, column=0)

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

		obs_password_entry = tk.Entry(self.master, textvariable=self.obs_password_text)
		obs_password_entry.grid(row=3, column=1)

		# Serial ports

		label = tk.Label(self.master, text='Select port')
		label.grid(row=4, column=0)

		empty_msg = 'Select port'

		self.serial_port_text = tk.StringVar(self.master)
		self.serial_port_text.set(self.interface.serial_port or empty_msg)

		def on_serial_connect():
			self.serial_port_text.set(self.interface.serial_port or empty_msg)
			self.serial_canvas.itemconfig(self.serial_light, fill='green')

		def on_serial_disconnect():
			self.serial_canvas.itemconfig(self.serial_light, fill='red')

		self.interface.connect_callback = on_serial_connect
		self.interface.disconnect_callback = on_serial_disconnect

		def set_serial_port(*_):
			if self.serial_port_text.get() != empty_msg:
				self.interface.serial_port = self.serial_port_text.get()

		self.serial_port_text.trace_add("write", set_serial_port)

		port_names = [p.device for p in self.interface.get_ports()]
		self.port_list = tk.OptionMenu(self.master, self.serial_port_text, *port_names)
		self.port_list.config(width=15)
		self.port_list.grid(row=4, column=1)

		def refresh_ports():
			self.serial_port_text.set(self.interface.serial_port or empty_msg)
			self.port_list['menu'].delete(0, 'end')
			new_choices = [p.device for p in self.interface.serial_ports]
			for choice in new_choices:
				self.port_list['menu'].add_command(label=choice, command=tk._setit(self.serial_port_text, choice))

		button = tk.Button(self.master, command=refresh_ports, text='Refresh')
		button.grid(row=5, column=1)

	def loop(self):
		self.master.mainloop()

if __name__ == '__main__':
	from dotenv import dotenv_values
	import sys
	env = dotenv_values()
	App().loop()