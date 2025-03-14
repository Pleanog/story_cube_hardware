import smbus2
import time
import RPi.GPIO as GPIO
import socket

# MPU-6050 Registers
MPU_ADDR = 0x68  # I2C address
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
TEMP_OUT_H = 0x41
GYRO_XOUT_H = 0x43

# Initialize I2C
bus = smbus2.SMBus(1)
bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)  # Wake up sensor

# Constants for shake detection
SHAKE_THRESHOLD = 1.5  # Threshold for shake magnitude (adjust as needed)
SHAKE_TIME_THRESHOLD = 0.5  # Minimum time between shakes (in seconds)

# Variables for shake detection
last_shake_time = time.time()
last_tap_time = time.time()

# Setup socket for communication with main.py
SOCKET_ADDRESS = ('localhost', 65433)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(SOCKET_ADDRESS)

def read_sensor_data():
    def read_word(reg):
        high = bus.read_byte_data(MPU_ADDR, reg)
        low = bus.read_byte_data(MPU_ADDR, reg + 1)
        value = (high << 8) + low
        return value - 65536 if value >= 0x8000 else value

    # Read accelerometer data
    accel_x = read_word(ACCEL_XOUT_H) / 16384.0  # Convert to g
    accel_y = read_word(ACCEL_XOUT_H + 2) / 16384.0
    accel_z = read_word(ACCEL_XOUT_H + 4) / 16384.0

    # Read temperature data
    temp_raw = read_word(TEMP_OUT_H)
    temperature = (temp_raw / 340.0) + 36.53  # Convert to °C

    # Read gyroscope data
    gyro_x = read_word(GYRO_XOUT_H) / 131.0  # Convert to degrees/s
    gyro_y = read_word(GYRO_XOUT_H + 2) / 131.0
    gyro_z = read_word(GYRO_XOUT_H + 4) / 131.0

    return accel_x, accel_y, accel_z, temperature, gyro_x, gyro_y, gyro_z

def determine_dice_face(ax, ay, az):
    """Determine which side is facing up based on acceleration."""
    threshold = 0.7  # g-force threshold
    if ax > threshold: return 1
    if ax < -threshold: return 2
    if ay > threshold: return 3
    if ay < -threshold: return 4
    if az > threshold: return 5
    if az < -threshold: return 6
    return 0  # Default if uncertain

def detect_shake(ax, ay, az):
    """Detect shake based on acceleration."""
    global last_shake_time
    
    # Calculate the magnitude of the acceleration vector
    shake_magnitude = (ax**2 + ay**2 + az**2)**0.5  # Pythagorean theorem for 3D magnitude
    
    current_time = time.time()
    
    # If the shake magnitude is above threshold and the time since last shake is sufficient
    if shake_magnitude > SHAKE_THRESHOLD and (current_time - last_shake_time) > SHAKE_TIME_THRESHOLD:
        last_shake_time = current_time  # Update last shake time
        return True
    return False


# Main function to listen for gyro data and print the current side
def gyro_handler():
    last_face = None
    while True:
        ax, ay, az, temp, gx, gy, gz = read_sensor_data()
        current_face = determine_dice_face(ax, ay, az)
        shaking = detect_shake(ax, ay, az)
        
        # Only send face updates if no shaking is detected
        if current_face != last_face and current_face != 0 and not shaking:
            print(f"Dice Face Up: {current_face}")
            last_face = current_face
            sock.sendall(f"face:{current_face}".encode())  # Send dice face to main.py

        if shaking:
            print("Shake detected! Preventing face change.")
            sock.sendall("shake:1".encode())  # Send shake signal to main.py

        time.sleep(0.5)  # Reduce update rate to avoid unnecessary checks

if __name__ == "__main__":
    try:
        gyro_handler()  # Run the gyro handler to detect and send data
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")
        sock.close()  # Close the socket connection on exit
        GPIO.cleanup()  # Clean up GPIO setup on program exit
