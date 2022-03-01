#!/usr/bin/env python3
import blemesh
try:
  from gi.repository import GLib
except ImportError:
  import glib as GLib
from dbus.mainloop.glib import DBusGMainLoop


import sys
import struct
import fcntl
import os
import numpy
import random
import dbus
import dbus.service
import dbus.exceptions

import paho.mqtt.client as mqtt
import time
import ssl
import os
import json

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


########################
# On Off Server Model
########################
class GatewayOnOffServer(blemesh.Model):
	def __init__(self, model_id):
		blemesh.Model.__init__(self, model_id)
		self.tid = None
		self.last_src = 0x0000
		self.last_dst = 0x0000
		self.cmd_ops = { 0x8201,  # get
				 0x8202,  # set
				 0x8203,  # set unacknowledged
				 0x8204 } # status

		print("OnOff Server ")
		self.state = 0
		blemesh.print_state(self.state)
		self.pub_timer = blemesh.ModTimer()
		self.t_timer = blemesh.ModTimer()

	def process_message(self, source, dest, key, data):
		datalen = len(data)

		if datalen != 3:
			# The opcode is not recognized by this model
			return

		opcode, state = struct.unpack('>HB',bytes(data))

		# print('opcode ' + opcode)

		if opcode != 0x8204 :
			# The opcode is not recognized by this model
			return

		print(set_yellow('Sending state '), end = '')

		state_str = "ON"
		if state == 0:
			state_str = "OFF"

		print(set_green(state_str), set_yellow('from'),
						set_green('%04x' % source))
		device = '%04x' % source
		print("topic: ble_gateway/" + device)
		#TODO Handle failures
		client.publish("ble_gateway/" + device, "{state:" + state_str + "}")

	def t_track(self):
			self.t_timer.cancel()
			self.tid = None
			self.last_src = 0x0000
			self.last_dst = 0x0000

	def set_publication(self, period):

		self.pub_period = period
		if period == 0:
			self.pub_timer.cancel()
			return

		# We do not handle ms in this example
		if period < 1000:
			return

		self.pub_timer.start(period/1000, self.publish)

	def publish(self):
		data = struct.pack('>HB', 0x8204, self.state)
		self.send_publication(data)


def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("Connected to Drogue cloud!")
		client.subscribe("command/inbox/#")
		client.on_message = on_message
	else:
		print("Failed to connect, return code %d\n", rc)

def on_publish(client, userdata, result):

	print("Published!")

def on_message(client, userdata, msg):
	print(msg.topic + " " + str(msg.payload))
	#TODO check command and target device

	state = -1
	command = json.loads(msg.payload.decode("utf-8"))
	if not command["state"] is None:
		if command["state"].lower() == "on":
			state = 1
		elif command["state"].lower() == "off":
			state = 0
		else:
			state = -1

	print("state: " + str(state))

	if state != -1:
		blemesh.app.elements[1].models[0].set_state(0x00aa, 0, state)

def main():
	global client

	token = os.environ.get('TOKEN')
	if token is None:
		print("'TOKEN' variable not set")
		sys.exit(1)

	blemesh.set_token(token)

	broker = os.environ.get('DROGUE_MQTT_HOST', 'mqtt.sandbox.drogue.cloud')
	port = os.environ.get('DROGUE_MQTT_PORT', 8883)

	username = os.environ.get('DROGUE_DEVICE', 'gateway@ble-demo')
	password = os.environ.get('DROGUE_PASSWORD', 'hey-rodney')

	print(set_yellow('Drogue endpint: ' + broker + ':' + str(port)))
	print(set_yellow('Drogue device: ' + username))

	client = mqtt.Client("drogue_gateway")
	client.on_connect = on_connect
	client.on_publish = on_publish
	client.username_pw_set(username, password)
	client.tls_set(cert_reqs=ssl.CERT_NONE)
	client.connect(broker, port)
	client.loop_start()


	DBusGMainLoop(set_as_default=True)
	blemesh.bus = dbus.SystemBus()
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
	first_ele.add_model(GatewayOnOffServer(0x1000))

	print(set_yellow('Register Vendor model on element 0'))
	first_ele.add_model(blemesh.SampleVendor(0x0001))

	print(set_yellow('Register OnOff Client model on element 1'))
	second_ele.add_model(blemesh.OnOffClient(0x1001))

	blemesh.app.add_element(first_ele)
	blemesh.app.add_element(second_ele)
	blemesh.mainloop = GLib.MainLoop()

	blemesh.attach(blemesh.token)
	blemesh.mainloop.run()


if __name__ == '__main__':
	main()