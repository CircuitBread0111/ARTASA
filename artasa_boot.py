#!/usr/bin/env python3
#//////////////////////////
#|File: artasa_boot.py
#|Author: Jerrin C. Redmon
#|Version: 1.0.0
#|Date: April 6, 2025
#//////////////////////////

# Description #
# A python script to prepare artasa for booting. This script
# provides an audible tts that a computer
# has been booted sucessfully and  prepares a push button to
# start the main program.

#-----------------------------------------------------------------

# Imports #
import time
import subprocess
import pyttsx3
from gpiozero import Button
from signal import pause


BUTTON_PIN = 16  # BCM pin
button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.3)
last_pressed = 0
cooldown = 5  


# Parameters #
speaker = pyttsx3.init() 			            

# Rate #
rate = speaker.getProperty('rate')  		# gets details of current speaking rate
speaker.setProperty('rate', 100)    		# sets new voice rate

# Volume #
volume = speaker.getProperty('volume')   	# gets the current volume level (min=0 and max=1)
speaker.setProperty('volume',1.0)  		# sets the volume level between 0 and 1

# Voice #
voices = speaker.getProperty('voices')		# gets details of current voice
speaker.setProperty('voice', voices[3].id)	# sets index for voice or language


# Boot message
speaker.say("Boot Successful")
speaker.runAndWait()
speaker.stop()
speaker.say("My name is ARTASA, your automated robotic text and speech assistant")
speaker.runAndWait()
speaker.stop()


def speak_and_run():
    global last_pressed
    now = time.time()
    if now - last_pressed >= cooldown:
        
        speaker.say("Please Present Item to Me")
        speaker.runAndWait()
        speaker.stop()
        
        try:
            subprocess.run(["python3", "/home/artasa/Desktop/Capstone/artasa_main.py"])  # Change path if needed
        except Exception as e:
            print(f"Error running script: {e}")
        
        last_pressed = now
    else:
        print("Ignored press due to cooldown")

button.when_pressed = speak_and_run

print("Waiting for button press...")
pause()





