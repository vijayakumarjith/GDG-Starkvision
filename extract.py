import os
import cv2
import numpy as np
import speech_recognition as sr
import pyttsx3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.core.window import Window
from keras.models import load_model
from kivy.config import Config
from kivy.graphics.texture import Texture
import PIL.Image

#Disable window resize
Config.set('graphics', 'resizable', False)
Window.size = (400, 600)

# Load the pre-trained model (this is not needed for speech to sign)
# classifier = load_model('model.h5', compile=False)
# image_x, image_y = 64, 64

# Function to classify and return the detected character (not needed for speech to sign)
# def give_char():
#     from keras.preprocessing import image
#     test_image = image.load_img('tmp1.png', target_size=(64, 64))
#     test_image = image.img_to_array(test_image)
#     test_image = np.expand_dims(test_image, axis=0)
#     result = classifier.predict(test_image)
#     chars = "ABCDEFGHIJKMNOPQRSTUVWXYZ"
#     indx = np.argmax(result[0])
#     return chars[indx]

# Function to check similarity
def check_sim(i, file_map):
    for item in file_map:
        for word in file_map[item]:
            if i == word:
                return 1, item
    return -1, ""

# Directory paths
op_dest = "alphabet"
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
                try:
                    im = PIL.Image.open(os.path.join(alpha_dest, str(j).lower() + "_small.gif"))
                    frameCnt = im.n_frames
                    for frame_cnt in range(frameCnt):
                        im.seek(frame_cnt)
                        im.save("tmp.png")
                        img = cv2.imread("tmp.png")
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        img = cv2.resize(img, (380, 260))
                        im_arr = img
                        all_frames.append((im_arr, 0.1))  # 100ms duration
                except FileNotFoundError:
                    print(f"File not found: {os.path.join(alpha_dest, str(j).lower() + '_small.gif')}")
                    pass  # Skip if the alphabet image is missing
        else:  # Handle `.webp` files
            try:
                im = PIL.Image.open(os.path.join(op_dest, sim))
                duration = 10  # 100ms
                if hasattr(im, "is_animated") and im.is_animated:
                    im.info.pop('background', None)
                    im.save('tmp.gif', 'gif', save_all=True)
                    im = PIL.Image.open("tmp.gif")
                    duration = im.info.get('duration', 100)/1000 # convert ms to sec
                frameCnt = im.n_frames if hasattr(im, "n_frames") else 1
                for frame_cnt in range(frameCnt):
                    im.seek(frame_cnt)
                    im.save("tmp.png")
                    img = cv2.imread("tmp.png")
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = cv2.resize(img, (380, 260))
                    im_arr = img
                    all_frames.append((im_arr, duration))
            except FileNotFoundError:
                print(f"File not found: {os.path.join(op_dest, sim)}")
                pass  # Skip if the .webp file is missing
    return all_frames

# Speech function
def speak(sentence):
    engine = pyttsx3.init()
    engine.say(sentence)
    engine.runAndWait()

class MainApp(App):
    def build(self):
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Voice to Sign UI
        voice_label = Label(text="Voice to Sign", font_size=20)
        main_layout.add_widget(voice_label)

        self.input_text = TextInput(hint_text='Enter text or record voice', multiline=False, font_size=14)
        main_layout.add_widget(self.input_text)

        voice_button = Button(text='Record Voice', font_size=16)
        voice_button.bind(on_press=self.hear_voice)
        main_layout.add_widget(voice_button)

        self.gif_image = Image()
        main_layout.add_widget(self.gif_image)

        return main_layout

    def hear_voice(self, instance):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                self.input_text.text = "Listening..."
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio).lower()

                # Replace "dot" with its equivalent representation
                text = text.replace("dot", ".")

                # Display detected text
                self.input_text.text = text

                # Automatically process and display sign language for the input text
                gif_frames = func(text)  # Generate frames for the sign language
                self.display_gif(gif_frames)  # Call the method to display GIFs

            except sr.UnknownValueError:
                self.input_text.text = "Could not understand the audio."
            except Exception as e:
                self.input_text.text = f"Error: {str(e)}"

    def display_gif(self, gif_frames):
        self.cnt = 0
        self.gif_frames = gif_frames
        self.gif_stream()

    def gif_stream(self):
        if self.cnt >= len(self.gif_frames):
            return
        img_array, duration = self.gif_frames[self.cnt]
        self.cnt += 1

        texture = Texture.create(size=(img_array.shape[1], img_array.shape[0]), colorfmt='rgb')
        texture.blit_buffer(img_array.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
        self.gif_image.texture = texture

        Clock.schedule_once(lambda dt: self.gif_stream(), duration)


if __name__ == '__main__':
    MainApp().run()