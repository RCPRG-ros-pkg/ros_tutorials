#!/usr/bin/env python
# encoding: utf8
import rospy
import turtlesim
from turtlesim.msg import Pose
from turtlesim.srv import SetPenRequest
from TurtlesimSIU import TurtlesimSIU
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from pynput.keyboard import Listener, Key
from math import cos, sin
import math
import signal
import sys
import numpy as np

# consts
VISUALIZE = True

linear_velocity = 0
rotation_velocity = 0

width = 4.5
length = 4

refresh_rate = 10

# RADIAN_CONVERSION = 0.0174532925
CENTER_TURTLE = 'center_turtle'

# state
currently_pressed = []
current_angle_in_rad = 0
center_x = 10
center_y = 10


def on_press(key):
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys
    if k not in currently_pressed:
        currently_pressed.append(k)


def on_release(key):
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys
    if k in currently_pressed:
        currently_pressed.remove(k)

    # stop on PAUSE
    if key == Key.pause:
        print("quit on PAUSE")
        return False


def signal_handler(sig, frame):
    print("Terminating")
    sys.exit(0)


def spawn_turtles():
    if turtle_api.hasTurtle(CENTER_TURTLE):
        turtle_api.killTurtle(CENTER_TURTLE)
    if not turtle_api.hasTurtle(CENTER_TURTLE):
        turtle_api.spawnTurtle(CENTER_TURTLE, turtlesim.msg.Pose(x=center_x, y=center_y, theta=current_angle_in_rad))

    # if turtle_api.hasTurtle('turtle2'):
    #     turtle_api.killTurtle('turtle2')
    # if not turtle_api.hasTurtle('turtle2'):
    #     turtle_api.spawnTurtle('turtle2', turtlesim.msg.Pose(x=base_x + length // 2, y=base_y + width // 2, theta=0))
    #
    # if turtle_api.hasTurtle('turtle3'):
    #     turtle_api.killTurtle('turtle3')
    # if not turtle_api.hasTurtle('turtle3'):
    #     turtle_api.spawnTurtle('turtle3', turtlesim.msg.Pose(x=base_x + length // 2, y=base_y - width // 2, theta=0))
    #
    # if turtle_api.hasTurtle('turtle4'):
    #     turtle_api.killTurtle('turtle4')
    # if not turtle_api.hasTurtle('turtle4'):
    #     turtle_api.spawnTurtle('turtle4', turtlesim.msg.Pose(x=base_x - length // 2, y=base_y + width // 2, theta=0))
    #
    # if turtle_api.hasTurtle('turtle5'):
    #     turtle_api.killTurtle('turtle5')
    # if not turtle_api.hasTurtle('turtle5'):
    #     turtle_api.spawnTurtle('turtle5', turtlesim.msg.Pose(x=base_x - length // 2, y=base_y - width // 2, theta=0))


def move_turtles():
    if len(currently_pressed) > 0:
        key = currently_pressed[0]
        if key == 'w':
            move_forward()
        elif key == 's':
            move_backward()
        elif key == 'a':
            turn_left()
        else:
            turn_right()


def render_turtles():
    turtle_api.setPose(turtle_name=CENTER_TURTLE,
                       pose=turtlesim.msg.Pose(x=center_x, y=center_y, theta=current_angle_in_rad), mode='absolute')


def move_forward():
    distance = linear_velocity / refresh_rate
    displacement = _rotate_vector([distance, 0])
    _move_center(displacement)


def move_backward():
    distance = linear_velocity / refresh_rate
    displacement = _rotate_vector([-distance, 0])
    _move_center(displacement)


def turn_left():
    rotation = rotation_velocity / refresh_rate
    global current_angle_in_rad
    current_angle_in_rad += rotation


def turn_right():
    rotation = rotation_velocity / refresh_rate
    global current_angle_in_rad
    current_angle_in_rad -= rotation


def _move_center(displacement):
    x = displacement[0]
    y = displacement[1]
    global center_x, center_y
    center_x += x
    center_y += y


def _rotate_vector(vector):
    rotation_matrix = np.array([[cos(current_angle_in_rad), -sin(current_angle_in_rad)],
                                [sin(current_angle_in_rad), cos(current_angle_in_rad)]])
    vector = np.array(vector)
    return np.dot(rotation_matrix, vector).tolist()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Not enough arguments")
        exit()
    else:
        linear_velocity = float(sys.argv[1])
        rotation_velocity = float(sys.argv[2])

    # Initialize ROS node
    signal.signal(signal.SIGINT, signal_handler)
    rospy.init_node('siu_example', anonymous=False)
    turtle_api = TurtlesimSIU.TurtlesimSIU()
    rate = rospy.Rate(refresh_rate)
    set_pen_req = turtlesim.srv.SetPenRequest(r=255, g=255, b=255, width=5, off=0)

    spawn_turtles()

    listener = Listener(on_press=on_press, on_release=on_release, suppress=False)
    listener.start()

    print(turtle_api.pixelsToScale())

    while listener.running and not rospy.is_shutdown():
        move_turtles()
        render_turtles()

        turtle_api.setPen('center_turtle', set_pen_req)
        rate.sleep()