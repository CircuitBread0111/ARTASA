#!/usr/bin/env python3
#//////////////////////////
#|File: artasa_boot.py
#|Author: Jerrin C. Redmon
#|Version: 0.1.0
#|Date: March 19, 2025
#//////////////////////////

# Description #
# A python script to prepare artasa for booting. This script
# provides an audible tts that a computer
# has been booted sucessfully and  pareparess a push button to
# start the main program.

#-----------------------------------------------------------------

# Imports #
import pyttsx3                      

# Parameters #
tts = pyttsx3.init() 			            # text-to-speech

# Rate #
rate = tts.getProperty('rate')  			# gets details of current speaking rate
tts.setProperty('rate', 100)    			# sets new voice rate

# Volume #
volume = tts.getProperty('volume')   		# gets the current volume level (min=0 and max=1)
tts.setProperty('volume',1.0)  				# sets the volume level between 0 and 1

# Voice #
voices = tts.getProperty('voices')			# gets details of current voice
tts.setProperty('voice', voices[3].id)		# sets index for voice or language

# Text_To_Speech #
def text_to_speech():

    tts.say("PC Boot Successful!")
    tts.runAndWait()
    tts.stop()

# Main #
if __name__ == "__main__":
    text_to_speech()
