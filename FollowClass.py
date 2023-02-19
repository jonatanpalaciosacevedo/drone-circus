import sys
import math
import imutils
import cv2
import tellopy
from assets import pose_module as pm
from simple_pid import PID
from pynput import keyboard
import threading
import os
import time
import datetime
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import av
import numpy as np
from PIL import ImageTk
from tkinter import messagebox


def put_text(frame, text, pos):
    cv2.putText(frame, text, (0, 30 + (pos * 30)),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)


def find_angle(p1, p2, p3, lmList):
    """
    Find the angle between 3 landmark points, given a list lmList with landmarks
    :param p1: point 1
    :param p2: point 2
    :param p3: point 3
    :param lmList: List with landmarks with the structure: lmList[int: Landmark][int: x or y pos]
    :return: Angle
    """
    # Get the landmarks
    x1, y1 = lmList[p1][1:]
    x2, y2 = lmList[p2][1:]
    x3, y3 = lmList[p3][1:]

    # Calculate the Angle
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) -
                         math.atan2(y1 - y2, x1 - x2))
    if angle < 0:
        angle += 360

    return angle


def find_distance(x1, y1, x2, y2):
    dist = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist


class FollowDetector:
    def __init__(self):

        # Drone state
        self.timestamp_take_picture = None
        self.keydown = False
        self.taken_off = False
        self.connected = False
        self.at_home = None
        self.drone = tellopy.Tello()
        self.flying = False
        self.detecting = False
        self.frame = None
        self.media_directory = "capturas"
        if not os.path.isdir(self.media_directory):
            os.makedirs(self.media_directory)
        self.date_fmt = '%Y-%m-%d_%H%M%S'

        # save video from drone uncomment to save video
        # self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        # self.out = cv2.VideoWriter('output.avi', self.fourcc, 10.0, (640, 480))

        # Detection values
        self.detector = pm.PoseDetector()
        self.pid_yaw = PID(0.25, 0, 0, setpoint=0, output_limits=(-100, 100))
        self.pid_throttle = PID(0.4, 0, 0, setpoint=0, output_limits=(-80, 100))
        self.pid_pitch = PID(0.4, 0, 0, setpoint=0, output_limits=(-50, 50))

        # Init drone
        self.battery = 0
        self.axis_command = {
            "yaw": self.drone.clockwise,
            "roll": self.drone.right,
            "pitch": self.drone.forward,
            "throttle": self.drone.up
        }
        self.axis_speed = {"yaw": 0, "roll": 0, "pitch": 0, "throttle": 0}
        self.cmd_axis_speed = {"yaw": 0, "roll": 0, "pitch": 0, "throttle": 0}
        self.prev_axis_speed = self.axis_speed.copy()
        self.def_speed = {"yaw": 50, "roll": 35, "pitch": 35, "throttle": 80}

    def buildFrame(self, fatherFrame):
        self.fatherFrame = fatherFrame

        self.cap = cv2.VideoCapture(0)

        self.master = tk.Frame(self.fatherFrame)
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)

        self.topFrame = tk.LabelFrame(self.master, text="Control")
        self.topFrame.columnconfigure(0, weight=1)
        self.topFrame.columnconfigure(1, weight=1)
        self.topFrame.rowconfigure(0, weight=1)
        self.topFrame.rowconfigure(1, weight=1)

        # state can be: initial, practising, flying, closed
        self.state = 'initial'

        # practice button
        self.practice = tk.Button(self.topFrame, text="Practica los movimientos", bg='#F57328', fg="white",
                                  command=self.practice)
        self.practice.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)
        self.closeButton = tk.Button(self.topFrame, text="Salir", bg='#FFE9A0', fg="black",
                                     command=self.close)
        self.closeButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

        # frame to be shown when practise is finish and user wants to fly
        self.buttonFrame = tk.Frame(self.topFrame)
        self.buttonFrame.rowconfigure(0, weight=1)
        self.buttonFrame.rowconfigure(1, weight=1)
        self.buttonFrame.columnconfigure(0, weight=1)
        self.buttonFrame.columnconfigure(1, weight=1)

        self.connectButton = tk.Button(self.buttonFrame, text="Connect", bg='#CC3636', fg="white", command=self.connect)
        self.connectButton.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

        self.takeOffButton = tk.Button(self.buttonFrame, text="Take Off", bg='#CC3636', fg="white",
                                       command=self.takeOff)
        self.takeOffButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

        # button to be shown when flying
        self.landButton = tk.Button(self.buttonFrame, text="Aterriza", bg='#CC3636', fg="white",
                                    command=self.returnHome)

        # button to be shown when the dron is back home
        self.closeButton2 = tk.Button(self.buttonFrame, text="Salir", bg='#FFE9A0', fg="black", command=self.close)

        self.topFrame.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

        # by defaulf, easy mode is selected
        self.bottomFrame = tk.LabelFrame(self.master, text="Indicaciones")

        self.image = Image.open("assets/follow_me.png")
        self.image = self.image.resize((400, 550), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        canvas1 = Canvas(self.bottomFrame, width=400, height=550)
        canvas1.pack(fill="both", expand=True)
        canvas1.create_image(0, 0, image=self.bg, anchor="nw")

        self.bottomFrame.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)

        return self.master

    def action(self):
        if self.connected:
            self.connectButton['text'] = 'connected'
            self.connectButton['bg'] = '#367E18'

        if self.taken_off:
            self.takeOffButton['text'] = 'flying'
            self.takeOffButton['bg'] = '#367E18'
            self.state = 'flying'
            self.reset()
            # this thread will start taking images and detecting patterns to guide the drone
            x = threading.Thread(target=self.main())
            x.start()
            self.landButton.grid(row=2, column=0, padx=5, columnspan=3, pady=5, sticky=N + S + E + W)

        if self.at_home:
            # the dron completed the RTL
            messagebox.showwarning("Success", "Ya hemos aterrizado", parent=self.master)
            self.landButton.grid_forget()

            # return to the initial situation
            """self.connectButton['bg'] = '#CC3636'
            self.connectButton['text'] = 'Connect'"""
            self.takeOffButton['bg'] = '#CC3636'
            self.takeOffButton['text'] = 'TakeOff'
            self.state = 'initial'

    def reset(self):
        self.axis_speed = {"yaw": 0, "roll": 0, "pitch": 0, "throttle": 0}
        self.cmd_axis_speed = {"yaw": 0, "roll": 0, "pitch": 0, "throttle": 0}
        self.prev_axis_speed = self.axis_speed.copy()
        self.def_speed = {"yaw": 50, "roll": 35, "pitch": 35, "throttle": 80}

    def on_press(self, keyname):
        """
            Handler for keyboard listener
        """
        if self.keydown:
            return
        try:
            self.keydown = True
            keyname = str(keyname).strip('\'')
            if keyname == 'Key.esc':
                self.drone.land()
                self.drone.quit()
                cv2.destroyAllWindows()
                os._exit(0)
            if keyname in self.controls_keypress:
                self.controls_keypress[keyname]()
        except AttributeError:
            print("Special key pressed")

    def on_release(self, keyname):
        """
            Reset on key up from keyboard listener
        """
        self.keydown = False
        keyname = str(keyname).strip('\'')
        if keyname in self.controls_keyrelease:
            key_handler = self.controls_keyrelease[keyname]()

    def set_speed(self, axis, speed):
        self.cmd_axis_speed[axis] = speed

    def take_picture(self):
        self.drone.take_picture()

    def init_controls(self):
        """
            Define keys and add listener
        """

        controls_keypress_QWERTY = {
            'w': lambda: self.set_speed("pitch", self.def_speed["pitch"]),
            's': lambda: self.set_speed("pitch", -self.def_speed["pitch"]),
            'a': lambda: self.set_speed("roll", -self.def_speed["roll"]),
            'd': lambda: self.set_speed("roll", self.def_speed["roll"]),
            'q': lambda: self.set_speed("yaw", -self.def_speed["yaw"]),
            'e': lambda: self.set_speed("yaw", self.def_speed["yaw"]),
            'i': lambda: self.drone.flip_forward(),
            'k': lambda: self.drone.flip_back(),
            'j': lambda: self.drone.flip_left(),
            'l': lambda: self.drone.flip_right(),
            'Key.left': lambda: self.set_speed("yaw", -1.5 * self.def_speed["yaw"]),
            'Key.right': lambda: self.set_speed("yaw", 1.5 * self.def_speed["yaw"]),
            'Key.up': lambda: self.set_speed("throttle", self.def_speed["throttle"]),
            'Key.down': lambda: self.set_speed("throttle", -self.def_speed["throttle"]),
            'Key.tab': lambda: self.drone.takeoff(),
            'Key.backspace': lambda: self.drone.land(),
            'Key.enter': lambda: self.take_picture(),
        }

        controls_keyrelease_QWERTY = {
            'w': lambda: self.set_speed("pitch", 0),
            's': lambda: self.set_speed("pitch", 0),
            'a': lambda: self.set_speed("roll", 0),
            'd': lambda: self.set_speed("roll", 0),
            'q': lambda: self.set_speed("yaw", 0),
            'e': lambda: self.set_speed("yaw", 0),
            'Key.left': lambda: self.set_speed("yaw", 0),
            'Key.right': lambda: self.set_speed("yaw", 0),
            'Key.up': lambda: self.set_speed("throttle", 0),
            'Key.down': lambda: self.set_speed("throttle", 0)
        }

        self.controls_keypress = controls_keypress_QWERTY
        self.controls_keyrelease = controls_keyrelease_QWERTY
        self.key_listener = keyboard.Listener(on_press=self.on_press,
                                              on_release=self.on_release)
        self.key_listener.start()

    def connect(self):
        self.closeButton2.grid_forget()
        self.init_drone()

    def takeOff(self):
        # do not allow taking off if not armed
        if self.connectButton['bg'] == '#367E18':
            self.drone.takeoff()
            self.taken_off = True
            self.flying = True
            self.detecting = True
            self.action()
        else:
            messagebox.showwarning("Error", "Antes de despegar debes conectarte al dron", parent=self.master)

    def returnHome(self):
        now = time.time()  # get the time
        self.drone.land()
        elapsed = time.time() - now
        time.sleep(3. - elapsed)

        self.at_home = True
        self.action()

    def init_drone(self):
        # Connect to the drone, start video
        self.drone.connect()
        self.drone.wait_for_connection(20.0)
        self.drone.start_video()
        self.drone.subscribe(self.drone.EVENT_FLIGHT_DATA,
                             self.flight_data_handler)
        self.drone.subscribe(self.drone.EVENT_FILE_RECEIVED,
                             self.handle_flight_received)
        self.container = av.open(self.drone.get_video_stream())
        self.connected = True
        self.init_controls()
        self.action()

    def flight_data_handler(self, event, sender, data):
        self.battery = data.battery_percentage

    def handle_flight_received(self, event, sender, data):
        """
            Create a file in local directory to receive image from the drone
        """
        path = f'{self.media_directory}/tello-{datetime.datetime.now().strftime(self.date_fmt)}.jpg'
        with open(path, 'wb') as out_file:
            out_file.write(data)

    def main(self):
        frame_skip = 300

        for frame in self.container.decode(video=0):
            if 0 < frame_skip:
                frame_skip = frame_skip - 1
                continue
            start_time = time.time()
            if frame.time_base < 1.0 / 60:
                time_base = 1.0 / 60
            else:
                time_base = frame.time_base

            # Convert frame to cv2 image
            frame = cv2.cvtColor(np.array(frame.to_image(), dtype=np.uint8), cv2.COLOR_RGB2BGR)
            frame = cv2.resize(frame, (640, 480))

            image = self.speed_controller(frame)

            # Uncomment if you want to save the Video
            # self.out.write(image)
            # Display the frame
            cv2.imshow('Tello', image)

            cv2.waitKey(1)

            frame_skip = int((time.time() - start_time) / time_base)

    def check_pose(self, lmList):
        if len(lmList) != 0:
            # Check if we detect a pose in the body detected by Openpose
            """
            left_arm_angle = detector.findAngle(img, 11, 13, 21)  # Brazo izquierdo
            right_arm_angle = detector.findAngle(img, 22, 14, 12)  # Brazo derecho
            left_arm_angle2 = detector.findAngle(img, 13, 11, 23)  # Brazo izquierdo
            right_arm_angle2 = detector.findAngle(img, 24, 12, 14)  # Brazo derecho
            """
            # Arms controls roll
            left_arm_angle = find_angle(11, 13, 21, lmList)
            left_arm_angle2 = find_angle(13, 11, 23, lmList)

            right_arm_angle = find_angle(22, 14, 12, lmList)
            right_arm_angle2 = find_angle(24, 12, 14, lmList)

            move_left = False
            move_right = False
            move_forward = False
            move_backward = False
            take_pic = False
            land_drone = False

            # Left arm up
            if 110 > left_arm_angle2 > 80 and 180 > left_arm_angle > 100:
                move_left = True

            # Right arm up
            if 110 > right_arm_angle2 > 80 and 180 > right_arm_angle > 100:
                move_right = True

            # Arms un and elbow folded
            if 110 > right_arm_angle2 > 80 and right_arm_angle < 50 and 110 > left_arm_angle2 > 80 and left_arm_angle < 50:
                take_pic = True

            # Wrists cross over head
            if left_arm_angle2 > 135 and 180 > left_arm_angle > 100 and right_arm_angle2 > 135 and 180 > right_arm_angle > 100:
                land_drone = True

            if move_left:
                return "MOVING_LEFT"

            if move_right:
                return "MOVING_RIGHT"

            if move_forward:
                return "MOVING_FORWARD"

            if move_backward:
                return "MOVING_BACKWARD"

            if take_pic:
                return "TAKING_PICTURE"

            if land_drone:
                return "LANDING_DRONE"

        else:
            return None

    def speed_controller(self, raw_frame):
        frame = raw_frame.copy()
        frame = imutils.resize(frame, height=480, width=640)
        h, w, _ = frame.shape

        ref_x = int(w / 2)
        ref_y = int(h * 0.4)

        self.axis_speed = self.cmd_axis_speed.copy()

        # If we are on the point to take a picture, the tracking is temporarily deactivated (2s)
        if self.timestamp_take_picture:
            if time.time() - self.timestamp_take_picture > 2:
                self.timestamp_take_picture = None
                self.take_picture()

        else:
            if self.detecting:
                frame = self.detector.findPose(frame, draw=True)
                lmList = self.detector.findPosition(frame, draw=True)
                self.pose = None

                if len(lmList) != 0:

                    # Do we recognize a predefined pose ?
                    self.pose = self.check_pose(lmList)

                    if self.pose:
                        # We trigger the associated action
                        if self.pose == "MOVING_RIGHT":
                            self.axis_speed["roll"] = -self.def_speed["roll"]

                        elif self.pose == "MOVING_LEFT":
                            self.axis_speed["roll"] = self.def_speed["roll"]

                        # elif self.pose == "MOVING_FORWARD":
                        #     self.axis_speed["pitch"] = self.def_speed["pitch"]

                        # elif self.pose == "MOVING_BACKWARD":
                        #     self.axis_speed["pitch"] = -self.def_speed["pitch"]

                        elif self.pose == "TAKING_PICTURE":
                            # Take a picture in 1 second
                            if self.timestamp_take_picture is None:
                                self.timestamp_take_picture = time.time()

                        elif self.pose == "LANDING_DRONE":
                            self.close()
                            self.action()

                    target = lmList[0]  # Nose landmark

                    if target:
                        # Calculate the xoff and yoff values for the PID controller (ROLL)
                        xoff = int(lmList[0][1] - ref_x)
                        yoff = int(ref_y - lmList[0][2])

                        # Calculate distance between shoulders to controll PITCH
                        right_shoulder_x = lmList[12][1]
                        left_shoulder_x = lmList[11][1]
                        shoulders_width = left_shoulder_x - right_shoulder_x
                        self.shoulders_width = shoulders_width
                        proximity = int(w / 3.1)
                        self.keep_distance = proximity

                        # Draw arrow to the nose to show the distance correction needed
                        cv2.circle(frame, (ref_x, ref_y), 15, (250, 150, 0), 1, cv2.LINE_AA)
                        cv2.arrowedLine(frame, (ref_x, ref_y), (target[1], target[2]), (250, 150, 0), 5)

                        # Face tracking PID controller
                        self.axis_speed["yaw"] = int(-self.pid_yaw(xoff))
                        self.axis_speed["throttle"] = int(-self.pid_throttle(yoff))
                        self.axis_speed["pitch"] = int(self.pid_pitch(self.shoulders_width - self.keep_distance))

        # Send commands to the drone
        if self.state == 'flying':
            for axis, command in self.axis_command.items():
                if self.axis_speed[axis] is not None and self.axis_speed[axis] != self.prev_axis_speed[axis]:
                    command(self.axis_speed[axis])
                    self.prev_axis_speed[axis] = self.axis_speed[axis]
                else:
                    # This line is necessary to display current values in 'self.^'
                    self.axis_speed[axis] = self.prev_axis_speed[axis]

        # Draw on HUD
        self.draw(frame)

        return frame

    def practice(self):
        if self.state == 'initial':
            # start practising
            self.practice['bg'] = '#367E18'
            self.practice['text'] = 'Estoy preparado. Quiero volar'
            self.state = 'practising'
            # startvideo stream to practice
            x = threading.Thread(target=self.practising)
            x.start()

        elif self.state == 'practising':
            # stop the video stream thread for practice
            self.state = 'closed'

            self.practice.grid_forget()

            # show buttons for connect, arm and takeOff
            self.buttonFrame.grid(row=1, column=0, columnspan=2, padx=5, pady=0, sticky=N + S + E + W)

            self.closeButton.grid_forget()
            self.closeButton.grid(row=0, column=0, columnspan=2, padx=7.5, pady=0, sticky=N + S + E + W)

    def practising(self):
        while self.state == 'practising':
            success, image = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            img = cv2.resize(image, (800, 600))
            h, w, _ = img.shape

            ref_x = int(w / 2)
            ref_y = int(h * 0.4)

            frame = self.detector.findPose(img, draw=True)
            lmList = self.detector.findPosition(img, draw=True)

            self.pose = None

            if len(lmList) != 0:

                # Do we recognize a predefined pose ?
                self.pose = self.check_pose(lmList)

                target = lmList[0]  # Nose landmark

                if target:
                    # Calculate the xoff and yoff values for the PID controller (ROLL)
                    xoff = int(lmList[0][1] - ref_x)
                    yoff = int(ref_y - lmList[0][2])

                    # Calculate distance between shoulders to controll PITCH
                    right_shoulder_x = lmList[12][1]
                    left_shoulder_x = lmList[11][1]
                    shoulders_width = left_shoulder_x - right_shoulder_x
                    self.shoulders_width = shoulders_width
                    proximity = int(w / 3.1)
                    self.keep_distance = proximity

                    # Draw arrow to the nose to show the distance correction needed
                    cv2.circle(frame, (ref_x, ref_y), 15, (250, 150, 0), 1, cv2.LINE_AA)
                    cv2.arrowedLine(frame, (ref_x, ref_y), (target[1], target[2]), (250, 150, 0), 5)

                    # Face tracking PID controller
                    # Commented so that it doesnt affect the dron when flying
                    """self.axis_speed["yaw"] = int(-self.pid_yaw(xoff))
                    self.axis_speed["throttle"] = int(-self.pid_throttle(yoff))
                    self.axis_speed["pitch"] = int(self.pid_pitch(self.shoulders_width - self.keep_distance))"""

            # Draw on HUD
            self.draw(frame)

            cv2.imshow('video', frame)
            cv2.waitKey(1)

        cv2.destroyWindow('video')
        cv2.waitKey(1)

    def draw(self, frame):
        bat = f"BAT: {int(self.battery)}"
        if self.axis_speed["throttle"] > 0:
            thr = f"ABAJO: {int(self.axis_speed['throttle'])}"
        else:
            thr = f"ARRIBA: {int(self.axis_speed['throttle'])}"
        if self.axis_speed["roll"] > 0:
            roll = f"DERECHA: {int(self.axis_speed['roll'])}"
        else:
            roll = f"IZQUIERDA: {int(self.axis_speed['roll'])}"
        if self.axis_speed["pitch"] > 0:
            pitch = f"ADELANTE: {int(self.axis_speed['pitch'])}"
        else:
            pitch = f"ATRAS: {int(self.axis_speed['pitch'])}"

        put_text(frame, bat, 0)
        put_text(frame, thr, 1)
        put_text(frame, roll, 2)
        put_text(frame, pitch, 3)
        put_text(frame, f"POSE: {self.pose}", 4)

    def landing(self):
        if self.flying:
            self.drone.land()
            self.flying = False

        self.at_home = True

    def close(self):
        if self.flying:
            self.drone.land()
            self.flying = False

        self.out.release()
        # this will stop the video stream thread
        self.state = 'closed'
        self.drone.quit()
        self.drone.sock.close()
        self.cap.release()
        self.at_home = True
        self.fatherFrame.destroy()
        cv2.destroyAllWindows()
        cv2.waitKey(1)
