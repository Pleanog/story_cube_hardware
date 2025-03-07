import RPi.GPIO as GPIO
import time
import socket

BUTTON_PIN = 26  # Adjust GPIO pin for your button
# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Setup socket for communication with main.py
SOCKET_ADDRESS = ('localhost', 65432)  # Main program socket address
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(SOCKET_ADDRESS)

def button_handler():
    last_state = GPIO.input(BUTTON_PIN)  # Start with the current state of the button
    debounce_time = 0.3  # Increase debounce time if needed
    
    while True:
        # time.sleep(1)  # Wait a bit to debounce
        current_state = GPIO.input(BUTTON_PIN)  # Read button state
        # print(f"Current state: {current_state}")

        if current_state != last_state:  # State change detected
            time.sleep(debounce_time)  # Wait a bit to debounce
            # Check state again after debounce time
            current_state = GPIO.input(BUTTON_PIN)  
            if current_state != last_state:  # Confirm state change
                if current_state == GPIO.LOW:  # Button pressed
                    print("Button pressed!(button_handler.py)")
                    sock.sendall("button_pressed".encode())
                else:  # Button released
                    print("Button released! (button_handler.py)")
                    sock.sendall("button_released".encode())
                
                last_state = current_state


if __name__ == "__main__":
    try:
        button_handler()
    except KeyboardInterrupt:
        GPIO.cleanup()  # Clean up GPIO on exit
