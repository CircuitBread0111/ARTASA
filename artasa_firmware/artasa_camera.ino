///////////////////////////|
//|File: artasa_camera.ino
//|Author: Jerrin C. Redmon
//|Language: C++
//|Version: 1.1.2 
//|Date: April 15, 2025
///////////////////////////|

/*
 * Description:
 * ARTASA Firmware
 * This firmware is designed to work with the Arducam Mega 5MP 
 * camera module. It captures images and sends them over serial 
 * to a connected device. Includes a buzzer that provides an audio 
 * cue when a picture is taken.The camera settings are configured 
 * for optimal performance for OCR. Designed to be used 
 * with the ESP32 microcontroller.
 */

//----------------------------------------------------------------

// Includes //
#include "Arducam_Mega.h"                                           // Arducam Camera Library

// Defines //
#define BUZZER 26                                                   // Buzzer Pin
#define FREQUENCY 2000                                              // PWM Frequency in Hz
#define RESOLUTION 8                                                // 8-bit resolution (0-255)
#define VOLUME 128                                                  // 8-bit Volume Control (0-255)
#define CS 17                                                       // Arducam Chip Select Pin

// Arducam//
Arducam_Mega Camera(CS);                                            // Create Camera Object

// Camera Settings //
CAM_IMAGE_MODE resolution = CAM_IMAGE_MODE_UXGA;                    // 1600x1200
CAM_IMAGE_PIX_FMT format = CAM_IMAGE_PIX_FMT_JPG;                   // JPEG Format

// Image Buffer //
const size_t buffer_size =0xff;                                     // 255 Hex
uint8_t image_buffer[buffer_size] = { 0 };                          // Image Buffer

// Setup //
void setup() {                                                         

  Serial.begin(921600);                                             // Set serial Baudrate to 921600
  delay(2000);                                                      // Delay for esp32 to begin serial
  ledcAttach(BUZZER, FREQUENCY, RESOLUTION);                        // Set Buzzer PWM Pin
  Camera.begin();                                                   // Initalize Camera
}

// Buzzer //
void buzzer(int t) {

  for (int i = 0; i < t; i++) {
    ledcWrite(BUZZER, VOLUME);                                      // Set Volume
    delay(150);                                                     // Sound Duration
    ledcWrite(BUZZER, 0);                                           // Turn off Buzzer       
    delay(150);                                                     // Delay between sounds   
  }
}

// Capture //
void capture() {

  buzzer(1);                                                        // Audio cue for taking a picture
  Camera.setAutoISOSensitive(0);                                    // Set Camera ISO to AUTO
  Camera.setAutoExposure(0);                                        // Set Camera Exposure to AUTO
  Camera.setAutoFocus(0);                                           // Set Camera Focus to AUTO 
  Camera.setColorEffect(CAM_COLOR_FX_BW);                           // B/W for increased legibility
  Camera.takePicture(resolution, format);                           // Takes a picture
  size_t image_size = Camera.getTotalLength();                      // Get image size 
  size_t bytes_read = 0;                                            // Total bytes read

  while (bytes_read < image_size) {                                 // Writing Image Over Serial
    size_t chunk_size = min(buffer_size, image_size - bytes_read);  // Read in chunks
    Camera.readBuff(image_buffer, chunk_size);                      // Read image data into buffer   
    Serial.write(image_buffer, chunk_size);                         // Write image data to serial 
    bytes_read += chunk_size;                                       // Increment bytes read
    delay(1);                                                       // Delay to prevent buffer overflow     
          
  }

  buzzer(2);                                                        // Audio cue for completion 
  Serial.println("DONE");                                           // Image transfer complete                                                 
}

// Loop //
void loop() {

  if (Serial.available()) {                                         // Check if serial is available
    
    String cmd = Serial.readStringUntil('\n');                      // New line character termination
    cmd.trim();                                                     // Remove whitespace
         
    if (cmd.equalsIgnoreCase("CAP")) {                              // Check for command 
      capture();                                                    // Capture image
    }

    else {                
      Serial.println("Unkown Command");                             // Command Unrecognized Error      
    }
  }
}

// EOF //
