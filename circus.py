import time
from tkinter import *
from pygame import mixer
import requests
from tkinter import font
from PIL import Image, ImageTk
from tkvideo import tkvideo
from DetectorClass import DetectorClass
from FollowClass import FollowDetector
import BodyControlClass


class Circo(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack()
        self.make_widgets()

    def make_widgets(self):
        # don't assume that self.parent is a root window.
        # instead, call `winfo_toplevel to get the root window
        self.winfo_toplevel().title("Circo de drones")


mixer.init()
mixer.music.load('assets/circo.mp3')
mixer.music.play(10)

root = Tk()
circo = Circo(root)
root.geometry("770x525")

image = Image.open("assets/entrada.png")
image = image.resize((770, 525), Image.ANTIALIAS)

bg = ImageTk.PhotoImage(image)
canvas1 = Canvas(root, width=770, height=525)
canvas1.pack(fill="both", expand=True)
canvas1.create_image(0, 0, image=bg, anchor="nw")

myFont = font.Font(family='Bernard MT Condensed', size=22, weight='bold')


def follow():
    mixer.music.stop()
    mixer.music.load('assets/aplausos.mp3')
    mixer.music.play(10)
    time.sleep(5)
    mixer.music.stop()

    newWindow = Toplevel(root)
    newWindow.title("Sígueme")
    newWindow.geometry("450x650")
    # Presentation mode
    # BodyControlClass.main()
    detector = FollowDetector()
    frame = detector.buildFrame(newWindow)
    frame.pack(fill="both", expand="yes", padx=10, pady=10)
    newWindow.mainloop()


def fingers():
    mixer.music.stop()
    mixer.music.load('assets/aplausos.mp3')
    mixer.music.play(10)
    time.sleep(5)
    mixer.music.stop()

    newWindow = Toplevel(root)
    newWindow.title("Dedos")
    newWindow.geometry("450x650")
    detector = DetectorClass()
    frame = detector.buildFrame(newWindow, 'fingers')
    frame.pack(fill="both", expand="yes", padx=10, pady=10)
    newWindow.mainloop()


def pose():
    mixer.music.stop()
    mixer.music.load('assets/aplausos.mp3')
    mixer.music.play(10)
    time.sleep(5)
    mixer.music.stop()

    newWindow = Toplevel(root)
    newWindow.title("Pose")
    newWindow.geometry("450x650")
    detector = DetectorClass()
    frame = detector.buildFrame(newWindow, 'pose')
    frame.pack(fill="both", expand="yes", padx=10, pady=10)
    newWindow.mainloop()


def faces():
    mixer.music.stop()
    mixer.music.load('assets/aplausos.mp3')
    mixer.music.play(10)
    time.sleep(5)
    mixer.music.stop()

    newWindow = Toplevel(root)
    newWindow.title("Pose")
    newWindow.geometry("450x650")
    detector = DetectorClass()
    frame = detector.buildFrame(newWindow, 'face')
    frame.pack(fill="both", expand="yes", padx=10, pady=10)
    newWindow.mainloop()


def bye():
    root.destroy()
    bye = Tk()
    circo1 = Circo(bye)
    bye.geometry("770x525")

    image = Image.open("assets/bye.png")
    image = image.resize((770, 525), Image.ANTIALIAS)
    bg = ImageTk.PhotoImage(image)
    canvas1 = Canvas(bye, width=770, height=525)
    canvas1.pack(fill="both", expand=True)

    canvas1.create_image(0, 0, image=bg, anchor="nw")

    bye.mainloop()


def enter():
    mixer.music.stop()
    mixer.music.load('assets/redoble.mp3')  # Loading Music File
    mixer.music.play(10)
    newWindow = Toplevel(root)
    newWindow.title("Selecciona un acto")
    newWindow.geometry("800x600")
    newWindow.columnconfigure(0, weight=1)
    newWindow.columnconfigure(1, weight=1)
    newWindow.columnconfigure(2, weight=1)
    newWindow.columnconfigure(3, weight=1)
    newWindow.rowconfigure(0, weight=1)
    newWindow.rowconfigure(1, weight=1)

    image2 = Image.open("assets/gallery.png")
    image2 = image2.resize((800, 520), Image.ANTIALIAS)
    bg2 = ImageTk.PhotoImage(image2)
    canvas2 = Canvas(newWindow, width=800, height=520)
    canvas2.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)
    canvas2.create_image(0, 0, image=bg2, anchor="nw")

    colorsButton = Button(newWindow, text="Follow Me", height=1, bg='#367E18', fg='#FFE9A0', width=12, command=follow)
    colorsButton.grid(row=0, column=0, padx=5, pady=5)
    colorsButton['font'] = myFont
    poseButton = Button(newWindow, text="Control Poses", height=1, bg='#367E18', fg='#FFE9A0', width=12, command=pose)
    poseButton.grid(row=0, column=1, padx=5, pady=5)
    poseButton['font'] = myFont
    fingersButton = Button(newWindow, text="Control Dedos", height=1, bg='#367E18', fg='#FFE9A0', width=12,
                           command=fingers)
    fingersButton.grid(row=0, column=2, padx=5, pady=5)
    fingersButton['font'] = myFont
    facesButton = Button(newWindow, text="Control Caras", height=1, bg='#367E18', fg='#FFE9A0', width=12, command=faces)
    facesButton.grid(row=0, column=3, padx=5, pady=5)
    facesButton['font'] = myFont

    byeButton = Button(newWindow, text="Salir", height=1, bg='#FFE9A0', fg='#367E18', command=bye)
    byeButton.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky=N + S + E + W)
    byeButton['font'] = myFont
    newWindow.mainloop()


enterButton = Button(root, text="Pasen y vean", height=1, bg='#367E18', fg='#FFE9A0', width=12, command=enter)
enterButton['font'] = myFont
enterButton_canvas = canvas1.create_window(770 / 2, 525 / 2 + 50, window=enterButton)

# Execute tkinter
root.mainloop()
