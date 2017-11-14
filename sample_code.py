#!/usr/bin/env python

import sys
import code
import readline
import rlcompleter
import socket
from bybop.Bybop_Discovery import *
import bybop.Bybop_Device

print 'Searching for devices'
discovery = Discovery([DeviceID.BEBOP_DRONE, DeviceID.JUMPING_SUMO])

discovery.wait_for_change()

devices = discovery.get_devices()

discovery.stop()

if not devices:
    print 'Oops ...'
    sys.exit(1)

device = devices.itervalues().next()

print 'Will connect to ' + get_name(device)

d2c_port = 54321
controller_type = "PC"
controller_name = "bybop shell"

drone = Bybop_Device.create_and_connect(
    device, d2c_port, controller_type, controller_name)

if drone is None:
    print 'Unable to connect to a product'
    sys.exit(1)

drone.dump_state()

vars = globals().copy()
vars.update(locals())
readline.set_completer(rlcompleter.Completer(vars).complete)
readline.parse_and_bind("tab: complete")
shell = code.InteractiveConsole(vars)

HOST = None               # Symbolic name meaning all available interfaces
PORT = 8888              # Arbitrary non-privileged port
s = None
for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
                              socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except socket.error, err_msg:
        print err_msg
        s = None
        continue
    try:
        s.bind(sa)
        s.listen(1)
    except socket.error, err_msg:
        print err_msg
        s.close()
        s = None
        continue
    break
if s is None:
    print 'could not open socket'
    sys.exit(1)

conn, addr = s.accept()
print 'Connected by', addr

while 1:
    data = conn.recv(1024)
    if not data:
        break
    if data == "t":
        drone.take_off()
    elif data == "e":
        drone.emergency()
    elif data == "l":
        drone.land()
    elif data == "w":
        drone.send_data('ARDrone3', 'Piloting', 'PCMD', True, 0, 50, 0, 0, 0)
    elif data == "s":
        drone.send_data('ARDrone3', 'Piloting', 'PCMD', True, 0, -50, 0, 0, 0)
    elif data == "a":
        drone.send_data('ARDrone3', 'Piloting', 'PCMD', True, -50, 0, 0, 0, 0)
    elif data == "d":
        drone.send_data('ARDrone3', 'Piloting', 'PCMD', True, 50, 0, 0, 0, 0)
    elif data == "q":
        drone.send_data('ARDrone3', 'Piloting', 'PCMD', True, 0, 0, 0, 50, 0)
    elif data == "z":
        drone.send_data('ARDrone3', 'Piloting', 'PCMD', True, 0, 0, 0, -50, 0)
    elif data == "x":
        drone.send_data('ARDrone3', 'Piloting', 'PCMD', True, 0, 0, 50, 0, 0)
    elif data == "c":
        drone.send_data('ARDrone3', 'Piloting', 'PCMD', True, 0, 0, -50, 0, 0)
    elif data == " ":
        drone.send_data('ARDrone3', 'Piloting', 'PCMD', True, 0, 0, 0, 0, 0)
    else:
        print 'Wrong Key'
    print data
conn.close()

drone.stop()
