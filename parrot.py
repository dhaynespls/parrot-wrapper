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
    devices = discovery.get_devices()
    discovery.stop()
    print "Found one!"
    return devices.itervalues().next()

def connect_to_the_drone(bebop_drone):
    """
    Establish a connection to the drone.

    Return a tuple of (BebopDrone, socket_connection)
    """
    print 'Will connect to ' + get_name(bebop_drone)
    d2c_port = 54321
    controller_type = "PC"
    controller_name = "bybop shell"
    print str(bebop_drone)
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
    return (drone, conn)

def fly_the_drone(drone_and_connection):
    """
    Until a SIGINT, fly the drone through the terminal.
    """

    try:
        while True:
            # drone_and_connection[1] is for the return conn from last connect_to_drone function. 
            data = drone_and_connection[1].recv(1024)
            if not data:
                break
            # drone_and_connection[0] is for the return value drone from last connect_to_drone function.
            if data == "t":
                drone_and_connection[0].take_off()
            elif data == "e":
                drone_and_connection[0].emergency()
            elif data == "l":
                drone_and_connection[0].land()

            # Pitch: pitch angle percentage (from -100 to 100).    
            elif data == "w":
                # Positive values go forward.
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 0, 50, 0, 0, 0)
            elif data == "s":
                # Negative values go backward.
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 0, -50, 0, 0, 0)

            # Roll: roll angle percentage (from -100 to 100).    
            elif data == "a":
                # Negative valules go left.
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, -50, 0, 0, 0, 0)
            elif data == "d":
                # Positive valules go right.
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 50, 0, 0, 0, 0)
             
            # Gaz: gaz speed percentage (calculated on the max vertical speed)(from -100 to 100).
            elif data == "i":
                # Positive values go up.
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 0, 0, 0, 50, 0)
            elif data == "k":
                # Negative values go down.
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 0, 0, 0, -50, 0)

            # Yaw: yaw speedpercentage (calculated on the max rotation speed)(from -100 to 100).
            elif data == "j":
                # Positive values go right.
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 0, 0, 50, 0, 0)
            elif data == "l":  
                # Negative values go left.
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 0, 0, -50, 0, 0)
            # Hover
            elif data == " ":
                # Stop moving and hover over the ground.
                drone_and_connection[0].send_data('ARDrone3', 'Piloting',
                                                  'PCMD', True, 0, 0, 0, 0, 0)
            # help message showing controls
            elif data == 'h':
                print 'Valid Keys:'
                print 't - take off'
                print 'e - emergency'
                print 'l - land'
                print 'w - forward'
                print 's - backward'
                print 'a - bank left'
                print 'd - bank right'
                print 'i - increase speed'
                print 'k - decrease speed'
                print 'j - pivot right'
                print 'l - pivot left'
                print '[space] - hover'
            else:
                print 'Invalid Key'
                print 'Press h to view valid keys'
                # Let the drone hover if it doesn't receive any control data or disconnected.
                # Otherwise, the drone will continue in its previous direction.
                # The reason we set back the values to 0 as soon as the keystrokes is released.
                drone_and_connection[0].send_data('ARDrone3','Piloting','PCMD', True, 0, 0, 0, 0, 0)
            print data

    #if user sends a keyboard interruption (Ctrl+C), disconnect from the drone
    except KeyboardInterrupt:
        drone_and_connection[1].close()
        drone_and_connection[0].stop()

# If executed, run main()
if __name__ == '__main__':
    main()
