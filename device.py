#!/usr/bin/env python3
import blemesh
try:
  from gi.repository import GLib
except ImportError:
  import glib as GLib
from dbus.mainloop.glib import DBusGMainLoop
import dbus
import dbus.service
import dbus.exceptions
import sys

try:
  from termcolor import colored, cprint
  set_error = lambda x: colored('!' + x, 'red', attrs=['bold'])
  set_cyan = lambda x: colored(x, 'cyan', attrs=['bold'])
  set_green = lambda x: colored(x, 'green', attrs=['bold'])
  set_yellow = lambda x: colored(x, 'yellow', attrs=['bold'])
except ImportError:
  print('!!! Install termcolor module for better experience !!!')
  set_error = lambda x: x
  set_cyan = lambda x: x
  set_green = lambda x: x
  set_yellow = lambda x: x


def main():

	DBusGMainLoop(set_as_default=True)
	blemesh.bus = dbus.SystemBus()

	if len(sys.argv) > 1 :
		blemesh.set_token(sys.argv[1])

	blemesh.mesh_net = dbus.Interface(blemesh.bus.get_object(blemesh.MESH_SERVICE_NAME,
						"/org/bluez/mesh"),
						blemesh.MESH_NETWORK_IFACE)

	blemesh.mesh_net.connect_to_signal('InterfacesRemoved', blemesh.interfaces_removed_cb)

	blemesh.app = blemesh.Application(blemesh.bus)

	# Provisioning agent
	blemesh.app.set_agent(blemesh.Agent(blemesh.bus))

	first_ele = blemesh.Element(blemesh.bus, 0x00)
	second_ele = blemesh.Element(blemesh.bus, 0x01)

	print(set_yellow('Register OnOff Server model on element 0'))
	first_ele.add_model(blemesh.OnOffServer(0x1000))

	print(set_yellow('Register Vendor model on element 0'))
	first_ele.add_model(blemesh.SampleVendor(0x0001))

	print(set_yellow('Register OnOff Client model on element 1'))
	second_ele.add_model(blemesh.OnOffClient(0x1001))

	blemesh.app.add_element(first_ele)
	blemesh.app.add_element(second_ele)

	blemesh.mainloop = GLib.MainLoop()

	print('Attaching')
	#blemesh.attach(int('62cb5d464413e5c7', 16))
	blemesh.attach(blemesh.token)
	blemesh.mainloop.run()


if __name__ == '__main__':
	main()