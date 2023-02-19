import threading
import time
import tkinter as tk
from tkinter import *
import cv2
from PIL import Image, ImageTk
import tellopy

from fingerDetector import FingerDetector
from poseDetector import PoseDetector
from faceDetector import FaceDetector
from PIL import ImageTk
from tkinter import messagebox


class DetectorClass:
    def __init__(self):
        self.direction = None
        self.returning = None
        self.RTL = False
        self.connected = False
        self.armed = None
        self.taken_off = None
        self.at_home = None

        self.takeoff_state = None
        self.drone = tellopy.Tello()
        self.battery = None

    def buildFrame(self, fatherFrame, mode):
        # mode can be: fingers, face or pose
        self.fatherFrame = fatherFrame
        self.mode = mode

        self.cap = cv2.VideoCapture(0)

        if self.mode == 'fingers':
            self.detector = FingerDetector()
        elif self.mode == 'pose':
            self.detector = PoseDetector()
        else:
            self.detector = FaceDetector()

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

        if self.mode == 'fingers':
            self.image = Image.open("assets/dedos_faciles.png")
        elif self.mode == 'pose':
            self.image = Image.open("assets/poses_faciles.png")
        else:
            self.image = Image.open("assets/caras_faciles.png")

        self.image = self.image.resize((400, 550), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        canvas1 = Canvas(self.bottomFrame, width=400, height=550)
        canvas1.pack(fill="both", expand=True)
        canvas1.create_image(0, 0, image=self.bg, anchor="nw")

        self.bottomFrame.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)

        return self.master

    def action(self):
        if self.connected:
            time.sleep(4)
            self.connectButton['text'] = 'connected'
            self.connectButton['bg'] = '#367E18'

        if self.taken_off:
            self.takeOffButton['text'] = 'flying'
            self.takeOffButton['bg'] = '#367E18'
            self.state = 'flying'
            # this thread will start taking images and detecting patterns to guide the drone
            x = threading.Thread(target=self.flying)
            x.start()
            self.landButton.grid(row=2, column=0, padx=5, columnspan=3, pady=5, sticky=N + S + E + W)

        if self.at_home:
            # the dron completed the RTL
            messagebox.showwarning("Success", "Ya estamos en casa", parent=self.master)
            self.landButton.grid_forget()

            # return to the initial situation
            self.connectButton['bg'] = '#CC3636'
            self.connectButton['text'] = 'Connect'
            self.takeOffButton['bg'] = '#CC3636'
            self.takeOffButton['text'] = 'TakeOff'
            self.state = 'initial'

    def connect(self):
        print('voy a conectar')
        # do not allow connection if level of difficulty is not fixed
        self.closeButton2.grid_forget()
        self.init_drone()

    def init_drone(self):
        # Connect to the drone, start streaming and subscribe to events
        self.drone.connect()
        self.drone.wait_for_connection(10.0)
        self.drone.send_packet_data("mon")
        self.drone.send_packet_data("mdirection 2")
        self.drone.subscribe(self.drone.EVENT_FLIGHT_DATA,
                             self.flight_data_handler)
        self.connected = True
        self.action()

    def flight_data_handler(self, event, sender, data):
        self.battery = data.battery_percentage

    def takeOff(self):
        # do not allow taking off if not armed
        if self.connectButton['bg'] == '#367E18':
            self.drone.takeoff()
            self.taken_off = True
            self.action()
        else:
            messagebox.showwarning("Error", "Antes de despegar debes conectarte al dron", parent=self.master)

    def close(self):
        # this will stop the video stream thread
        self.state = 'closed'
        self.cap.release()
        self.drone.sock.close()
        self.drone.quit()
        self.fatherFrame.destroy()
        cv2.destroyAllWindows()
        cv2.waitKey(1)

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

    def __setDirection(self, code):
        if code == 1:
            return 'Adelante'
        elif code == 2:
            return 'Atras'
        elif code == 3:
            return 'Derecha'
        elif code == 4:
            return 'Izquierda'
        elif code == 5:
            return 'Flip'
        elif code == 6:
            return 'Aterriza'
        elif code == 0:
            return 'Stop'
        else:
            return ''

    def practising(self):
        # when the user changes the pattern (new face, new pose or new fingers) the system
        # waits some time (ignore 8 video frames) for the user to stabilize the new pattern
        # we need the following variables to control this
        prevCode = -1
        cont = 0

        while self.state == 'practising':
            success, image = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue

            code, img = self.detector.detect(image)
            img = cv2.resize(img, (800, 600))
            img = cv2.flip(img, 1)

            # if user changed the pattern we will ignore the next 8 video frames
            if (code != prevCode):
                cont = 4
                prevCode = code
            else:
                cont = cont - 1
                if cont < 0:
                    # the first 8 video frames of the new pattern (to be ignored) are done
                    # we can start showing new results
                    direction = self.__setDirection(code)
                    cv2.putText(img, direction, (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 10)

            cv2.imshow('video', img)
            cv2.waitKey(1)
        cv2.destroyWindow('video')
        cv2.waitKey(1)

    def flying(self):
        # see comments for practising function
        prevCode = -1
        cont = 0
        # we need to know if the dron is returning to lunch to show an apropriate message
        self.returning = False

        self.direction = ''
        while self.state == 'flying':
            if not self.returning:
                success, image = self.cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    # If loading a video, use 'break' instead of 'continue'.
                    continue
                code, img = self.detector.detect(image)
                img = cv2.resize(img, (800, 600))
                img = cv2.flip(img, 1)

                if (code != prevCode):
                    cont = 8
                    prevCode = code
                else:
                    cont = cont - 1
                    if cont < 0:
                        self.direction = self.__setDirection(code)

                        if code == 1:   # north
                            self.drone.forward(30)
                        elif code == 2:  # south
                            self.drone.backward(30)
                        elif code == 3:  # east
                            self.drone.right(30)
                        elif code == 4:  # west
                            self.drone.left(30)
                        elif code == 5:
                            self.drone.send_packet_data("flip b")
                        elif code == 6:
                            self.returnHome()
                        elif code == 0:
                            self.drone.forward(0)
                            self.drone.backward(0)
                            self.drone.right(0)
                            self.drone.left(0)

                cv2.putText(img, self.direction, (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 10)
                cv2.imshow('video', img)
                cv2.waitKey(1)

            else:
                cv2.destroyWindow('video')
                cv2.waitKey(1)
                break

    def returnHome(self):
        self.returning = True
        self.direction = 'Aterrizando'
        now = time.time()  # get the time
        self.drone.land()
        elapsed = time.time() - now
        time.sleep(3. - elapsed)

        self.at_home = True
        self.action()

