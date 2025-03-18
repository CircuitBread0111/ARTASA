#!/usr/bin/env python3
#//////////////////////////
#|File: artasa_test.py
#|Author: Jerrin C. Redmon
#|Version: 1.0
#|Date: March 12, 2025
#//////////////////////////

# Description #
# 
# 
# 

#-----------------------------------------------------------------

# Imports #
import serial
import time
import cv2
import easyocr as ocr
import pyttsx3 as tts


# Serial Settings #
port = "/dev/ttyUSB0"   # Name of selected serial port
baudrate = 921600       # Baudrate of seleted port

# OCR Settings #
language = "en"         # Sets language to english

# File Outputs #
image_output = "/home/Jerrin/Desktop/Capstone/image_output.jpg"
ocr_output = "/home/Jerrin/Desktop/Capstone/ocr_output.txt" 
output_file = "image_output.jpg"

# Initalize #
ocr_reader = ocr.Reader([language])
print(f"OCR Initalized!\nSelected Language:{language}")


## TTS Settings ###

speaker = tts.init()
print("tts initalized!")

# RATE #
rate = speaker.getProperty('rate')  			# gets details of current speaking rate
speaker.setProperty('rate', 125)    			# sets new voice rate

# VOLUME #
volume = speaker.getProperty('volume')   		# gets the current volume level (min=0 and max=1)
speaker.setProperty('volume',1.0)  				# sets the volume level between 0 and 1

# VOICE #
voices = speaker.getProperty('voices')			# gets details of current voice
speaker.setProperty('voice', voices[1].id)		# sets index for voice or language



#-----------------------------------------------------------------



def send_commands(srl):

    srl.write(b"CAP\n")
    print("Command Sent")
    time.sleep(3)



#-----------------------------------------------------------------



def serial_read(srl):

    buffer = bytearray()
    recieving = False
    start = False

    print(f"Reading {port}...")
    

    with open(output_file, "wb") as file:
        
        while (True):

            image_data = srl.read(1) #read one byte at a time
            if (not image_data):
                continue

            if ((not start and image_data) == b'\xFF'):
                soi_byte = srl.read(1)
                if (soi_byte == b"\xD8"):
                    print("SOI FOUND")
                    buffer = bytearray()
                    recieving = True
                    start = True
                    continue

            elif (recieving):
                buffer.append(image_data[0])

                if ((image_data == b'\xD9') and (len(buffer)>2) and (buffer[-2] == 0xFF)):
                    print("EOI FOUND")
                    file.write(buffer)
                    print("IMAGE SAVED")
                    break



#-----------------------------------------------------------------



def ocr_function(input_image_path):

    
    print("Proecessing Image...\n")
    input_image = cv2.imread(image_output)
    ocr_results = ocr_reader.readtext(input_image_path)
    print("Image Processed!")
    print("=" *40 + "\n")


    with open (ocr_output, "w") as text_file:
        
        for (bbox, text, prob) in ocr_results:
            if prob > 0.75:
                print(f"Text: {text}\nCofidence: {prob:.3f}\n")

            #TODO add condition for only words with over 50% Prob
                text_file.write(f"{text} ")

    print("=" *40 + "\n")
    print(f"Detected text saved in {ocr_output}")



#-----------------------------------------------------------------



def text_to_speech(file_path):

    with open(file_path, "r") as file:
        text = file.read().strip()
        speaker.say(text)
        speaker.runAndWait()
        speaker.stop()


 #-----------------------------------------------------------------



if __name__ == "__main__":
    
    with serial.Serial(port, baudrate) as srl:
        time.sleep(2)
        send_commands(srl)
        serial_read(srl)
        srl.close()
    
    ocr_function(image_output)
    text_to_speech(ocr_output)