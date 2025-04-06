import numpy as np
import cv2
import os
import PIL
from PIL import ImageTk
import PIL.Image
import speech_recognition as sr
import pyttsx3
import tkinter as tk
from tkinter import *
from keras.models import load_model
from tkinter import messagebox

# Load the pre-trained model
classifier = load_model('model.h5', compile=False)
image_x, image_y = 64, 64

# Function to classify and return the detected character
def give_char():
    from keras.preprocessing import image
    test_image = image.load_img('tmp1.png', target_size=(64, 64))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis=0)
    result = classifier.predict(test_image)
    chars = "ABCDEFGHIJKMNOPQRSTUVWXYZ"
    indx = np.argmax(result[0])
    return chars[indx]

# Function to check similarity
def check_sim(i, file_map):
    for item in file_map:
        for word in file_map[item]:
            if i == word:
                return 1, item
    return -1, ""

# Directory paths
op_dest = "filtered_data"
alpha_dest = "alphabet"

dirListing = os.listdir(op_dest)
editFiles = [item for item in dirListing if ".webp" in item]

# File map creation
file_map = {}
for i in editFiles:
    tmp = i.replace(".webp", "").split()
    file_map[i] = tmp

# Function to create frames for GIF animations
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
                    all_frames.append((im_arr, 2000))  # 1-second duration for alphabet images
        else:  # Handle `.webp` files
            im = PIL.Image.open(os.path.join(op_dest, sim))
            duration = 750
            if hasattr(im, "is_animated") and im.is_animated:
                im.info.pop('background', None)
                im.save('tmp.gif', 'gif', save_all=True)
                im = PIL.Image.open("tmp.gif")
                duration = im.info.get('duration', 100)
            frameCnt = im.n_frames if hasattr(im, "n_frames") else 1
            for frame_cnt in range(frameCnt):
                im.seek(frame_cnt)
                im.save("tmp.png")
                img = cv2.imread("tmp.png")
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (380, 260))
                im_arr = PIL.Image.fromarray(img)
                all_frames.append((im_arr, duration))
    return all_frames

# Speech function
def speak(sentence):
    engine = pyttsx3.init()
    engine.say(sentence)
    engine.runAndWait()

# GUI Class
class Tk_Manage(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self, bg="lightblue")
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

# Home Page
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="lightblue")
        label = tk.Label(self, text="Two-Way Sign Language Translator", font=("Verdana", 16, "bold"), bg="lightblue")
        label.pack(pady=20)
        button = tk.Button(self, text="Voice to Sign", font=("Verdana", 12), command=lambda: controller.show_frame(VtoS), bg="blue", fg="white")
        button.pack(pady=10)
        button2 = tk.Button(self, text="Sign to Voice", font=("Verdana", 12), command=lambda: controller.show_frame(StoV), bg="blue", fg="white")
        button2.pack(pady=10)

# Voice to Sign Page
class VtoS(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="lightblue")
        label = tk.Label(self, text="Voice to Sign", font=("Verdana", 16, "bold"), bg="lightblue")
        label.pack(pady=20)

        # Input and buttons
        self.inputtxt = tk.Text(self, height=4, width=30, font=("Verdana", 10))
        voice_button = tk.Button(self, text="Record Voice", font=("Verdana", 10), command=self.hear_voice, bg="green", fg="white")
        self.gif_box = tk.Label(self, bg="lightblue")

        # Layout
        self.inputtxt.pack(pady=10)
        voice_button.pack(pady=5)
        self.gif_box.pack(pady=20)

    def hear_voice(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                self.inputtxt.delete("1.0", tk.END)
                self.inputtxt.insert(tk.END, "Listening...")
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio).lower()
                
                # Replace "dot" with its equivalent representation
                text = text.replace("dot", ".")
                
                # Display detected text in the text box
                self.inputtxt.delete("1.0", tk.END)
                self.inputtxt.insert(tk.END, text)
                
                # Automatically process and display sign language for the input text
                gif_frames = func(text)  # Generate frames for the sign language
                self.display_gif(gif_frames)  # Call the method to display GIFs

            except sr.UnknownValueError:
                messagebox.showerror("Error", "Could not understand the audio.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def display_gif(self, gif_frames):
        global cnt
        cnt = 0
        self.gif_frames = gif_frames
        self.gif_stream()

    def gif_stream(self):
        global cnt
        if cnt >= len(self.gif_frames):
            return
        img, duration = self.gif_frames[cnt]
        cnt += 1
        imgtk = ImageTk.PhotoImage(image=img)
        self.gif_box.imgtk = imgtk
        self.gif_box.configure(image=imgtk)
        self.gif_box.after(duration, self.gif_stream)

# Sign to Voice Page
class StoV(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="lightblue")
        label = tk.Label(self, text="Sign to Voice", font=("Verdana", 16, "bold"), bg="lightblue")
        label.pack(pady=20)
        disp_txt = tk.Text(self, height=4, width=30, font=("Verdana", 10))
        disp_txt.pack()
        button1 = tk.Button(self, text="Back to Home", font=("Verdana", 12), command=lambda: controller.show_frame(StartPage), bg="blue", fg="white")
        button1.pack()

        def start_video():
            video_frame = tk.Label(self, bg="lightblue")
            cam = cv2.VideoCapture(0)

            def video_stream():
                ret, frame = cam.read()
                frame = cv2.flip(frame, 1)
                img_name = "tmp1.png"
                save_img = cv2.resize(frame[102:298, 427:623], (image_x, image_y))
                cv2.imwrite(img_name, save_img)
                disp_txt.insert(tk.END, give_char())
                img = PIL.Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                video_frame.imgtk = imgtk
                video_frame.configure(image=imgtk)
                video_frame.after(1, video_stream)

            video_stream()
            video_frame.pack()

        start_vid = tk.Button(self, text="Start Video", font=("Verdana", 12), command=start_video, bg="green", fg="white")
        start_vid.pack()

# Run the app
app = Tk_Manage()
app.geometry("800x600")
app.mainloop()
