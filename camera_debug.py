import serial
import time

# Update these as needed
port = "/dev/ttyUSB0"
baudrate = 921600
timeout = 5
image_output = "image_output.jpg"

def send_commands(srl):
    srl.reset_input_buffer()  # Clear out old junk
    srl.write(b"CAP\n")
    print("Sent CAP command")

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
                print(f"Received {len(buffer)} bytes...")

            if len(buffer) >= 2 and buffer[-2:] == b'\xFF\xD9':
                print("[✓] EOI FOUND")
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

if __name__ == "__main__":
    with serial.Serial(port, baudrate, timeout=timeout) as srl:
        time.sleep(2)  # Allow serial to settle
        send_commands(srl)
        serial_read(srl)
        wait_for_done(srl)
