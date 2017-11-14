#!/usr/bin/env python2
"""
parrot.py

Your controller should be able to issue the following commands:

1) Take off and hover.
2) Land.
3) Adjust its roll (left/right tilt), pitch (front/back tilt). (You may refer
to http://forum.developer.parrot.com/t/roll-pitch-yaw-rotation-convention/59)

Python 2 my dude, I'm sorry.
"""
# Python standard lib imports
import sys
import code
import readline
import rlcompleter
import socket

# Third party imports
from bybop.Bybop_Discovery import DeviceID, Discovery, get_name
from bybop.Bybop_Device import create_and_connect

def main():
    """
    Call functions and alert the user as to what's going on.
    """
    print "### Getting the Drone object"
    # A dictionary containing information about the first drone we found.
    the_bebop_drone = discover_the_drone()
    # Make a connection to the drone and get a tuple back with connection
    # stuff.
    print "### Connecting to the Drone"
    drone_and_connection = connect_to_the_drone(the_bebop_drone)
    # Until a SIGINT, fly the drone through the terminal.
    print "### Flying the Drone"
    fly_the_drone(drone_and_connection)

def discover_the_drone():
    """
    Search the network for Bebop drones and return the first one.

    Return a dictionary containing "service" details about the first drone we
    find.
    """
    print 'Searching for devices'
    discovery = Discovery([DeviceID.BEBOP_DRONE])
    discovery.wait_for_change()
    discovery.stop()
    print "Found one!"
    return discovery.get_devices()[0]

def connect_to_the_drone(bebop_drone):
    """
    Establish a connection to the drone.

    Return a tuple of (BebopDrone, socket_connection)
    """
    print 'Will connect to ' + get_name(bebop_drone)
    d2c_port = 54321
    controller_type = "PC"
    controller_name = "bybop shell"
    drone = create_and_connect(bebop_drone, d2c_port, controller_type,
                               controller_name)
    if drone is None:
        print 'Unable to connect to a product'
        sys.exit(1)
    drone.dump_state()

    vars = globals().copy()
    vars.update(locals())
    readline.set_completer(rlcompleter.Completer(vars).complete)
    readline.parse_and_bind("tab: complete")
    shell = code.InteractiveConsole(vars)

    # Symbolic name meaning all available interfaces
    HOST = None
    # Arbitrary non-privileged port
    PORT = 8888
    # Variable representing the socket
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
    return (conn, drone)

def fly_the_drone(drone_and_connection):
    """
    Until a SIGINT, fly the drone through the terminal.
    """
    try:
        while True:
            data = drone_and_connection[1].recv(1024)
            if not data:
                break
            if data == "t":
                drone_and_connection[0].take_off()
            elif data == "e":
                drone_and_connection[0].emergency()
            elif data == "l":
                drone_and_connection[0].land()
            elif data == "w":
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 0, 50, 0, 0, 0)
            elif data == "s":
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 0, -50, 0, 0, 0)
            elif data == "a":
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, -50, 0, 0, 0, 0)
            elif data == "d":
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 50, 0, 0, 0, 0)
            elif data == "q":
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 0, 0, 0, 50, 0)
            elif data == "z":
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 0, 0, 0, -50, 0)
            elif data == "x":
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 0, 0, 50, 0, 0)
            elif data == "c":
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 0, 0, -50, 0, 0)
            elif data == " ":
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 0, 0, 0, 0, 0)
            else:
                print 'Wrong Key'
            print data
    except KeyboardInterrupt:
        drone_and_connection[1].close()
        drone_and_connection[0].stop()

# If executed, run main()
if __name__ == '__main__':
    main()
