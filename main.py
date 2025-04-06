import numpy as np
import cv2
import os
import PIL
from PIL import ImageTk
import PIL.Image
import speech_recognition as sr
from tkinter import *
import time
from keras.models import load_model

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    import Tkinter as tk
    from Tkinter import messagebox

classifier = load_model('model.h5', compile=False)

image_x, image_y = 64, 64

def give_char():
    from keras.preprocessing import image
    test_image = image.load_img('tmp1.png', target_size=(64, 64))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis=0)
    result = classifier.predict(test_image)
    chars = "ABCDEFGHIJKMNOPQRSTUVWXYZ"
    indx = np.argmax(result[0])
    return chars[indx]

def check_sim(i, file_map):
    for item in file_map:
        for word in file_map[item]:
            if i == word:
                return 1, item
    return -1, ""

op_dest = "filtered_data"
alpha_dest = "alphabet"

dirListing = os.listdir(op_dest)
editFiles = [item for item in dirListing if ".webp" in item]

file_map = {}
for i in editFiles:
    tmp = i.replace(".webp", "").split()
    file_map[i] = tmp

def func(a):
    all_frames = []
    words = a.split()

    for i in words:
        flag, sim = check_sim(i, file_map)
        if flag == -1:  # Handle alphabet images
            for j in i:
                im = PIL.Image.open(os.path.join(alpha_dest, str(j).lower() + "_small.gif"))
                frameCnt = im.n_frames
                for frame_cnt in range(frameCnt):
                    im.seek(frame_cnt)
                    im.save("tmp.png")
                    img = cv2.imread("tmp.png")
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = cv2.resize(img, (380, 260))
                    im_arr = PIL.Image.fromarray(img)
                    all_frames.append((im_arr, 1000))  # 1-second duration for alphabet images
        else:  # Handle `.webp` files
            im = PIL.Image.open(os.path.join(op_dest, sim))
            duration = 1000  # Default to 1-second delay for static images
            if hasattr(im, "is_animated") and im.is_animated:  # Check for animation
                im.info.pop('background', None)
                im.save('tmp.gif', 'gif', save_all=True)
                im = PIL.Image.open("tmp.gif")
                duration = im.info.get('duration', 100)  # Use native frame duration if available
            frameCnt = im.n_frames if hasattr(im, "n_frames") else 1
            for frame_cnt in range(frameCnt):
                im.seek(frame_cnt)
                im.save("tmp.png")
                img = cv2.imread("tmp.png")
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (380, 260))
                im_arr = PIL.Image.fromarray(img)
                all_frames.append((im_arr, duration))  # Append duration with the frame

    return all_frames

class Tk_Manage(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (StartPage, VtoS, StoV):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Two Way Sign Language Translator", font=("Verdana", 12))
        label.pack(pady=10, padx=10)
        button = tk.Button(self, text="Voice to Sign", command=lambda: controller.show_frame(VtoS))
        button.pack()
        button2 = tk.Button(self, text="Sign to Voice", command=lambda: controller.show_frame(StoV))
        button2.pack()

class VtoS(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Voice to Sign", font=("Verdana", 12))
        label.pack(pady=10, padx=10)
        gif_box = tk.Label(self)

        def gif_stream():
            global cnt
            global gif_frames
            if cnt >= len(gif_frames):
                return
            img, duration = gif_frames[cnt]  # Extract frame and duration
            cnt += 1
            imgtk = ImageTk.PhotoImage(image=img)
            gif_box.imgtk = imgtk
            gif_box.configure(image=imgtk)
            gif_box.after(duration, gif_stream)  # Use dynamic frame duration

        def hear_voice():
            store = sr.Recognizer()
            with sr.Microphone() as s:
                audio_input = store.record(s, duration=10)
                try:
                    text_output = store.recognize_google(audio_input)
                    inputtxt.insert(END, text_output)
                except:
                    inputtxt.insert(END, '')

        def Take_input():
            INPUT = inputtxt.get("1.0", "end-1c")
            global gif_frames
            gif_frames = func(INPUT)
            global cnt
            cnt = 0
            gif_stream()
            gif_box.place(x=400, y=160)

        l = tk.Label(self, text="Enter Text or Voice:")
        l1 = tk.Label(self, text="OR")
        inputtxt = tk.Text(self, height=4, width=25)
        voice_button = tk.Button(self, height=2, width=20, text="Record Voice", command=hear_voice)
        voice_button.place(x=50, y=180)
        Display = tk.Button(self, height=2, width=20, text="Convert", command=Take_input)
        l.place(x=50, y=160)
        l1.place(x=115, y=230)
        inputtxt.place(x=50, y=250)
        Display.pack()

class StoV(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Sign to Voice", font=("Verdana", 12))
        label.pack(pady=10, padx=10)
        button1 = tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(StartPage))
        button1.pack()
        button2 = tk.Button(self, text="Voice to Sign", command=lambda: controller.show_frame(VtoS))
        button2.pack()

        disp_txt = tk.Text(self, height=4, width=25)

        def start_video():
            video_frame = tk.Label(self)
            cam = cv2.VideoCapture(0)

            global img_counter
            img_counter = 0
            global img_text
            img_text = ''

            def video_stream():
                global img_text
                global img_counter
                if img_counter > 200:
                    return
                img_counter += 1
                ret, frame = cam.read()
                frame = cv2.flip(frame, 1)
                img = cv2.rectangle(frame, (425, 100), (625, 300), (0, 255, 0), thickness=2)
                imcrop = frame[102:298, 427:623]
                hsv = cv2.cvtColor(imcrop, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, np.array([35, 10, 0]), np.array([160, 230, 255]))
                img_name = "tmp1.png"     
                save_img = cv2.resize(mask, (image_x, image_y))
                cv2.imwrite(img_name, save_img)
                tmp_text = img_text[:]
                img_text = give_char()
                if tmp_text != img_text:
                    disp_txt.insert(END, tmp_text)
                img = PIL.Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                video_frame.imgtk = imgtk
                video_frame.configure(image=imgtk)
                video_frame.after(1, video_stream)

            video_stream()
            disp_txt.pack()
            video_frame.pack()

        start_vid = tk.Button(self, height=2, width=20, text="Start Video", command=start_video)
        start_vid.pack()

app = Tk_Manage()
app.geometry("800x750")
app.mainloop()
