#!/usr/bin/env python3
#//////////////////////////
#|File: artasa_main.py
#|Author: Jerrin C. Redmon
#|Version: 1.3.2 
#|Date: April 15, 2025
#//////////////////////////

# Description # 
# This script is designed to work with the ESP32 firmware
# Sends a command to the ESP32 camera module to capture an image
# and uses PaddleOCR to extract text from the image. The extracted
# text is then converted to speech using the Piper TTS engine.
# The script is designed to be run on a Raspberry Pi with a serial
# connection to the ESP32 camera module. 

#-----------------------------------------------------------------

# Imports #
import serial                                                                                                                   # Serial library for serial communication
import time                                                                                                                     # Time library for sleep and delay functions                               
import os                                                                                                                       # OS library for file path handling
import subprocess                                                                                                               # Subprocess library for running shell commands
import cv2                                                                                                                      # OpenCV library for image processing                       
from paddleocr import PaddleOCR                                                                                                 # PaddleOCR library for Optical Character Recognition

# Serial Settings #
port = "/dev/ttyUSB0"                                                                                                           # Serial port for ESP32 camera module                           
baudrate = 921600                                                                                                               # Baudrate for serial communication
timeout = 5                                                                                                                     # Timeout for serial communication      

# OCR Settings #
language = "en"                                                                                                                 # Language for OCR

#File Paths #
image_output = "/home/artasa/Desktop/artasa_master/image_output.jpg"                                                            # Path to save the captured image
ocr_output = "/home/artasa/Desktop/artasa_master/ocr_output.txt"                                                                # Path to save the OCR output
output_file = "image_output.jpg"                                                                                                # Output file name for the captured image   
MODEL_PATH = "/home/artasa/piper_models/en_US/en_US-joe-medium.onnx"                                                            # Path to the model (Joe)
CONFIG_PATH = "/home/artasa/piper_models/en_US/en_US-joe-medium.onnx.json"                                                      # Path to the config file
OUTPUT_WAV = "artasa_output.wav"                                                                                                # Output wav file name

# Initialize #
ocr_reader = PaddleOCR(use_angle_cls=True, lang=language)                                                                       # Initialize PaddleOCR with the specified language


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


# Send Commands #
def send_commands(srl):                                                                                                         # Function to send commands to the ESP32 camera module

    srl.reset_input_buffer()                                                                                                    # Clear the input buffer
    srl.write(b"CAP\n")                                                                                                         # Send command to capture image
   
                        
# Serial Read #
def serial_read(srl):                                                                                                           # Function to read data from the serial port

    buffer = bytearray()                                                                                                        # Initialize buffer to store incoming data
    receiving = False                                                                                                           # Flag to indicate if we are receiving data                    

    with open(image_output, "wb") as file:                                                                                      # Open the output file to save the image

        while (True):                                                                                                           # Loop until we find the end of the image
            byte = srl.read(1)                                                                                                  # Read one byte from the serial port

            if (not byte):                                                                                                      # Check if no byte is received                    
                print("Timeout or no data.")                                                                                    # Print timeout message
                continue                                                                                                        # Continue to the next iteration

            if (not receiving):                                                                                                 # Check if we are not currently receiving data

                if (byte == b'\xFF'):                                                                                           # Check if the byte is the start of an image
                    next_byte = srl.read(1)                                                                                     # Read the next byte

                    if (next_byte == b'\xD8'):                                                                                  # Check if the next byte is the start of an image                         
                        buffer = bytearray(b'\xFF\xD8')                                                                         # Initialize buffer with SOI bytes
                        receiving = True                                                                                        # Set receiving flag to True
                continue                                                                                                        # Continue to the next iteration

            buffer.extend(byte)                                                                                                 # Append the received byte to the buffer    
 
            if (len(buffer) >= 2 and buffer[-2:] == b'\xFF\xD9'):                                                               # Check if the last two bytes are EOI
                file.write(buffer)                                                                                              # Write the buffer to the output file
                break                                                                                                           # Break the loop if EOI is found


# Wait for Done #
def wait_for_done(srl):                                                                                                         # Function to wait for DONE message from ESP32  

    done = srl.readline().decode(errors='ignore').strip()                                                                       # Read the DONE message from the serial port

    if (done == "DONE"):                                                                                                        # Check if the message is DONE
        print("\n")                                                                                                             # Print empty line            

    else:                                                                                                                       # If the message is not DONE    
        print("Move On", done)                                                                                                  # Print the message received


# OCR Function #
def ocr_function(input_image_path):                                                                                             # Function to perform OCR on the captured image
   
    ocr_results = ocr_reader.ocr(input_image_path, cls=True)                                                                	# Perform OCR on the image                           

    with open(ocr_output, "w") as text_file:                                                                                   	# Open the output file to save the OCR results

        for result in ocr_results:                                                                                              # Loop through the OCR results      
            
            for line in result:                                                                                                 # Loop through each line in the result       
                
                bbox, (text, prob) = line                                                                                       # Unpack the bounding box and text/probability

                if (prob > 0.75):                                                                                              	# Check if the probability is above the threshold    

                    print(f"Text: {text}\nConfidence: {prob:.3f}\n")                                                            # Print the detected text and confidence
                    text_file.write(f"{text} ")                                                                                 # Write the detected text to the output file


# Text to Speech #
def text_to_speech(file_path):                                                                                                  # Function to convert text to speech using Piper TTS engine

    if not (os.path.exists(file_path)):                                                                                         # Check if the OCR output file exists
        
        print("OCR output file not found.")                                                                                     # Print error message
        return                                                                                                                  # Return if file not found

    with open(file_path, "r") as file:                                                                                          # Open the OCR output file to read the text

        text = file.read().strip()                                                                                              # Read the text from the file

        if not (text):                                                                                                          # Check if the text is empty
            say("Processing complete. No text was detected.")                                                                   # Print message if no text detected

        else:
            say("Processing complete. This is what I found.")                                                                   # Print message indicating text found
            say(text)                                                                                                           # Convert the detected text to speech                     


# Main Function #
if __name__ == "__main__":                                                                                                      # Main function to run the script
    
    with serial.Serial(port, baudrate) as srl:                                                                                  # Open the serial port with the specified settings

        time.sleep(1)                                                                                                           # Wait for the serial port to initialize
        send_commands(srl)                                                                                                      # Send command to capture image                      
        serial_read(srl)                                                                                                        # Read the image data from the serial port
        wait_for_done(srl)                                                                                                      # Wait for DONE message from ESP32
        srl.close()                                                                                                             # Close the serial port           
    
    ocr_function(image_output)                                                                                                  # Perform OCR on the captured image                                                                                                                                                
    text_to_speech(ocr_output)                                                                                                 	# Convert the detected text to speech

# EOF #
