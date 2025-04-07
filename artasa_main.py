#!/usr/bin/env python3
#//////////////////////////
#|File: artasa_main.py
#|Author: Jerrin C. Redmon
#|Version: 1.2.0  
#|Date: April 7, 2025
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
from paddleocr import PaddleOCR
import pyttsx3 as tts


# Serial Settings #
port = "/dev/ttyUSB0"   # Name of selected serial port
baudrate = 921600       # Baudrate of seleted port
timeout = 5 		# Timeout for serial port


# OCR Settings #
language = "en"         # Sets language to english

# File Outputs #
image_output = "/home/artasa/Desktop/Capstone/image_output.jpg"
ocr_output = "/home/artasa/Desktop/Capstone/ocr_output.txt" 
output_file = "image_output.jpg"

# Initalize #
ocr_reader = PaddleOCR(use_angle_cls=True, lang=language)
print(f"OCR Initalized!\nSelected Language:{language}")


## TTS Settings ###
speaker = tts.init()
print("tts initalized!")

# Rate #
rate = speaker.getProperty('rate')  			# gets details of current speaking rate
speaker.setProperty('rate', 100)    			# sets new voice rate

# Volume #
volume = speaker.getProperty('volume')   		# gets the current volume level (min=0 and max=1)
speaker.setProperty('volume',1.0)  				# sets the volume level between 0 and 1

# Voice #
voices = speaker.getProperty('voices')			# gets details of current voice
speaker.setProperty('voice', voices[3].id)		# sets index for voice or language



#-----------------------------------------------------------------



def send_commands(srl):

    srl.reset_input_buffer()
    srl.write(b"CAP\n")
    print("Command Sent")
    



#-----------------------------------------------------------------



def serial_read(srl):
    buffer = bytearray()
    receiving = False

    print("Waiting for SOI...")

    with open(image_output, "wb") as file:
        while True:
            byte = srl.read(1)
            if not byte:
                print("Timeout or no data.")
                continue

            if not receiving:
                if byte == b'\xFF':
                    next_byte = srl.read(1)
                    if next_byte == b'\xD8':
                        print("[✓] SOI FOUND")
                        buffer = bytearray(b'\xFF\xD8')
                        receiving = True
                continue

            buffer.extend(byte)

            if len(buffer) % 1024 == 0:
                print(f"Received {len(buffer)} bytes")

            if len(buffer) >= 2 and buffer[-2:] == b'\xFF\xD9':
                print("[✓] EOI FOUND")
                print(f"Image Size {len(buffer) / 1000} KB")
                file.write(buffer)
                print(f"Image saved to {image_output}")
                break


def wait_for_done(srl):
    print("Waiting for DONE message...")
    done = srl.readline().decode(errors='ignore').strip()
    if done == "DONE":
        print("[✓] Arduino confirmed completion.")
    else:
        print("[!] Unexpected end message:", done)              





#-----------------------------------------------------------------



def ocr_function(input_image_path):

    
    print("Proecessing Image...\n")
    input_image = cv2.imread(input_image_path)
    ocr_results = ocr_reader.ocr(input_image_path, cls=True)  # Using PaddleOCR
    print("Image Processed!")
    print("=" *40 + "\n")


    with open(ocr_output, "w") as text_file:
        for result in ocr_results:
            for line in result:
                bbox, (text, prob) = line
                if prob > 0.75: # 5% cofidence change later
                    print(f"Text: {text}\nConfidence: {prob:.3f}\n")
                    text_file.write(f"{text} ")

    print("=" *40 + "\n")
    print(f"Detected text saved in {ocr_output}")



#-----------------------------------------------------------------



def text_to_speech(file_path):

    with open(file_path, "r") as file:
        text = file.read().strip()
        speaker.say("Processing Complete! This is what I found!.")
        speaker.runAndWait()
        speaker.stop()
        speaker.say(text)
        speaker.runAndWait()
        speaker.stop()


 #-----------------------------------------------------------------



if __name__ == "__main__":
    
    with serial.Serial(port, baudrate) as srl:
        time.sleep(1)
        send_commands(srl)
        serial_read(srl)
        wait_for_done(srl)
        srl.close()
    
    ocr_function(image_output)
    time.sleep(1)
    text_to_speech(ocr_output)




