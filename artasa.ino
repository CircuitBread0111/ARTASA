///////////////////////////|
//|File: artasa.ino
//|Author: Jerrin C. Redmon
//|Language: C++
//|Version: 1.0.0
//|Date: March 23, 2025
///////////////////////////|

/*
 * Description:
 * ARTASA Firmware
 * 
 */

//----------------------------------------------------------------

// INCLUDES //
#include "Arducam_Mega.h"                                           // Arducam Camera Library

// DEFINES //
#define BUZZER 26                                                   // Buzzer Pin
#define FREQUENCY 1000                                              // PWM Frequency in Hz
#define RESOLUTION 8                                                // 8-bit resolution (0-255)
#define VOLUME 128                                                  // 8-bit Volume Control (0-255)
#define CS 17                                                       // Arducam Chip Select Pin

// ARDUCAM //
Arducam_Mega Camera(CS);

// CAMERA SETTINGS //
CAM_IMAGE_MODE resolution = CAM_IMAGE_MODE_UXGA;                    // 1600x1200
CAM_IMAGE_PIX_FMT format = CAM_IMAGE_PIX_FMT_JPG;                   // JPEG Format
CAM_COLOR_FX black_white = CAM_IMAGE_FX_BW;                         // Black and White Images

// IMAGE BUFFER //
const size_t buffer_size = 0xff;                                    // 255 Hex
uint8_t image_buffer[buffer_size] = { 0 };

// SETUP //
void setup() {

  Serial.begin(921600);                                             // Set serial Baudrate to 921600
  delay(2000);                                                      // Delay for esp32 to begin serial
  ledcAttach(BUZZER, FREQUENCY, RESOLUTION);                        // Set Buzzer PWM Pin
  Camera.begin();                                                   // Initalize Camera

}

// BUZZER //
void buzzer() {

  for (int i = 0; i < 2; i++) {
    ledcWrite(BUZZER, VOLUME);
    delay(150);                                                     // Sound Duration
    ledcWrite(BUZZER, 0);
    delay(150);
  }

}

// CAPTURE //
void capture() {

  delay(100);                                                       // Delay before taking the picture
  buzzer();                                                         // Audio cue for taking a picture

  Camera.setAutoISOSensitive(0);                                    // Set Camera ISO to AUTO
  Camera.setAutoExposure(0);                                        // Set Camera Exposure to AUTO
  Camera.setAutoFocus(0);                                           // Set Camera Focus to AUTO
  Camera.setColorEffect(black_white);                               // Set Camera Color to B&W

Camera.setColorEffect(CAM_COLOR_FX_BW);                             // B/W for increased legibility

  Camera.takePicture(resolution, format);                           // Takes a picture
  
  size_t image_size = Camera.getTotalLength();
  size_t bytes_read = 0;                                            // Total bytes read

  Serial.flush();                        
  delay(500);                                                       // Delay for flush serial

  Serial.write(0xFF);                                               // JPEG SOI Byte 1
  Serial.write(0xD8);                                               // JPEG SOI Byte 2

  while (bytes_read < image_size) {                                 // Writing Image Over Serial

    size_t chunk_size = min(buffer_size, image_size - bytes_read); 
    Camera.readBuff(image_buffer, chunk_size);
    Serial.write(image_buffer, chunk_size);
    bytes_read += chunk_size;
    delay(5);

  }

  Serial.write(0xFF);                                               // JPEG EOI Byte 1
  Serial.write(0xD9);                                               // JPEG EOI Byte 2
  Serial.flush();
  delay(500);                                                       // Delay for flush serial

}

// LOOP //
void loop() {

  if (Serial.available()) {                                         // Check if serial is available

    String cmd = Serial.readStringUntil('\n');                      // New line character termination
    cmd.trim();

    if (cmd.equalsIgnoreCase("CAP")) {                              // Check for commands
      capture();
    }
    else {
      Serial.println("Unkown Command");
    }
  }
}
