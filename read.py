import os
import cv2
import numpy as np
import speech_recognition as sr
import pyttsx3
import streamlit as st
from PIL import Image
from keras.models import load_model

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

# Function to check similarity
def check_sim(i, file_map):
    for item in file_map:
        for word in file_map[item]:
            if i == word:
                return 1, item
    return -1, ""

# Function to create frames for GIF animations
def func(a):
    all_frames = []
    words = a.split()
    for i in words:
        flag, sim = check_sim(i, file_map)
        if flag == -1:  # Handle alphabet images
            for j in i:
                try:
                    im = Image.open(os.path.join(alpha_dest, str(j).lower() + "_small.gif"))
                    frameCnt = im.n_frames
                    for frame_cnt in range(frameCnt):
                        im.seek(frame_cnt)
                        im_arr = np.array(im)
                        all_frames.append(im_arr)
                except FileNotFoundError:
                    print(f"File not found: {os.path.join(alpha_dest, str(j).lower() + '_small.gif')}")
                    pass
        else:  # Handle `.webp` files
            try:
                im = Image.open(os.path.join(op_dest, sim))
                frameCnt = im.n_frames if hasattr(im, "n_frames") else 1
                for frame_cnt in range(frameCnt):
                    im.seek(frame_cnt)
                    im_arr = np.array(im)
                    all_frames.append(im_arr)
            except FileNotFoundError:
                print(f"File not found: {os.path.join(op_dest, sim)}")
                pass
    return all_frames

# Speech recognition
def record_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            st.info("Listening...")
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio).lower()
            return text.replace("dot", ".")
        except sr.UnknownValueError:
            return "Could not understand the audio."
        except Exception as e:
            return f"Error: {str(e)}"

# Text-to-speech
def speak(sentence):
    engine = pyttsx3.init()
    engine.say(sentence)
    engine.runAndWait()

# Streamlit app
def main():
    st.title("Voice to Sign Language Converter")
    
    # Input and button for recording voice
    st.markdown("### Enter Text or Record Your Voice:")
    input_text = st.text_input("Input Text:", "")
    if st.button("Record Voice"):
        input_text = record_voice()
        st.write(f"Detected Text: {input_text}")
    
    # Generate and display frames for sign language
    if input_text:
        gif_frames = func(input_text)
        if gif_frames:
            st.image(gif_frames, width=300, caption="Sign Language Translation")
        else:
            st.warning("No matching GIF frames found!")

if __name__ == "__main__":
    main()
