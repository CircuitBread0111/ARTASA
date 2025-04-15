#!/usr/bin/env python3
#//////////////////////////
#|File: artasa_boot.py
#|Author: Jerrin C. Redmon
#|Version: 1.1.1
#|Date: April 15, 2025
#//////////////////////////

# Description #
# A python script to prepare artasa for booting. This script
# provides an audible text-to-speech that is
# has been booted sucessfully and prepares a push button to
# start the main program.

#-----------------------------------------------------------------

# Imports #
import time                                                                                                                     # Import time for sleep and delay functions
import subprocess                                                                                                               # Import subprocess for running shell commands                        
from gpiozero import Button                                                                                                     # GPIO library for button handling                               
from signal import pause                                                                                                        # Signal library for pausing the program

# File Paths #
MODEL_PATH = "/home/artasa/piper_models/en_US/en_US-joe-medium.onnx"                                                            # Path to the model (Joe)
CONFIG_PATH = "/home/artasa/piper_models/en_US/en_US-joe-medium.onnx.json"                                                      # Path to the config file
OUTPUT_WAV = "artasa_tts.wav"                                                                                                   # Output wav file name

# Button Setup #
BUTTON_PIN = 16                                                                                                                 # GPIO pin number for the button       
button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.3)                                                                      # Button setup with pull-up resistor and debounce time
last_pressed = 0                                                                                                                # Last button press time                                
cooldown = 5                                                                                                                    # Cooldown between button presses (seconds)


# Say #
def say(text):                                                                                                                  # Function to convert text to speech using Piper TTS engine

    try:
        p1 = subprocess.Popen(                                                                                                                         
            ["/home/artasa/.local/bin/piper", "--model", MODEL_PATH, "--config", CONFIG_PATH, "--output_file", OUTPUT_WAV],                                                
            stdin=subprocess.PIPE)                                                                                              # Popen to run piper with the model and config file                                                                                                                
        p1.communicate(input=text.encode("utf-8"))                                                                              # Send text to piper                                           
        subprocess.run(["aplay", OUTPUT_WAV])                                                                                   # Play the output wav file using aplay
                                                             
    except Exception as e:                                                                                                      # Exception handling for subprocess errors
        print(f"Error running piper: {e}")                                                                                      # Print error message if subprocess fails                    


# Boot Sequence #
say("Boot successful!")                                                                                                         # Print boot message
say("My name is ARTASA, your automated robotic text and speech assistant.")                                                     # Print name message                      
say("Please press the button to start the main program.")                                                                       # Print button message
                 
                     
# Button Handler #
def Button_Handler():                                                                                                           # Button handler function

    global last_pressed                                                                                                         # Access the global variable last_pressed
    now = time.time()                                                                                                           # Get the current time                                           
                                                                       
    if (now - last_pressed >= cooldown):                                                                                        # Check if the cooldown period has passed   
        say("Please show item to me.")                                                                                          # Print item message                          

        try:
            subprocess.run(["python3", "/home/artasa/Desktop/artasa_master/artasa_main.py"])                                    # Run the main program script

        except Exception as e:   
            print(f"Error running script: {e}")                                                                                 # Print error message if script fails

        last_pressed = now                                                                                                      # Update last_pressed to current time                                    

    else:                                                                                          
        print("Ignored press due to cooldown")                                                                                  # Print ignored message if button press is within cooldown period


# Button Lisenser #
button.when_pressed = Button_Handler                                                                                            # Assign the button handler 
print("Waiting for button press...")                                                                                            # Print waiting message
pause()                                                                                                                         # Pause the program

# EOF #                                          