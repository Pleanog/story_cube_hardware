import smbus2 as smbus
import time
import math
import RPi.GPIO as GPIO
from neopixel import NeoPixel
from board import D18

MPU_ADDR = 0x68  # Default I2C address for the MPU-6050 (can be 0x69 if AD0 is high)

# Set up PWM on GPIO 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 1000)  # 1000 Hz PWM frequency
pwm.start(0)  # Start with 0% duty cycle (off)

# Initialize I2C bus and MPU-6050 sensor
bus = smbus.SMBus(1)
address = 0x68  # MPU-6050 I2C address

# Wake up MPU-6050
bus.write_byte_data(address, 0x6B, 0)

# Set up LED strip on GPIO 18
led_pin = D18  # Pin for NeoPixel
num_pixels = 5  # Only 1 LED for this example
strip = NeoPixel(led_pin, num_pixels, brightness=1, auto_write=True)

# Colors for the dice sides (RGB)
colors = {
    1: (255, 0, 0),    # Red
    2: (0, 255, 0),    # Green
    3: (0, 0, 255),    # Blue
    4: (255, 255, 0),  # Yellow
    5: (255, 165, 0),  # Orange
    6: (255, 255, 255),# White
}

def twos_complement(val):
    if val >= 0x8000:  # 0x8000 is the value for 32768, the limit for signed 16-bit integers
        val -= 0x10000  # Subtract 65536 (2^16) to convert to a negative signed value
    return val

def read_gyro():
    # Read raw gyro values for X, Y, and Z
    x = bus.read_word_data(MPU_ADDR, 0x43)  # 0x43 is the address for X-axis high byte
    y = bus.read_word_data(MPU_ADDR, 0x45)  # 0x45 is the address for Y-axis high byte
    z = bus.read_word_data(MPU_ADDR, 0x47)  # 0x47 is the address for Z-axis high byte
    
    # Convert to signed 16-bit integer
    x = twos_complement(x)
    y = twos_complement(y)
    z = twos_complement(z)
    
    return x, y, z


def read_accel():
    # Read raw acceleration values for X, Y, and Z
    ax = bus.read_word_data(MPU_ADDR, 0x3B)  # 0x3B is the address for X-axis high byte
    ay = bus.read_word_data(MPU_ADDR, 0x3D)  # 0x3D is the address for Y-axis high byte
    az = bus.read_word_data(MPU_ADDR, 0x3F)  # 0x3F is the address for Z-axis high byte
    
    # Convert to signed 16-bit integers
    ax = twos_complement(ax)
    ay = twos_complement(ay)
    az = twos_complement(az)
    
    return ax, ay, az


def read_temp():
    # Read raw temperature value
    temp = bus.read_word_data(MPU_ADDR, 0x41)  # 0x41 is the address for temperature high byte
    
    # Convert to signed 16-bit integer
    temp = twos_complement(temp)
    
    # Convert to temperature in Celsius (this might require calibration)
    temp = temp / 340.0 + 36.53  # For MPU6050, temperature is scaled by 340 and offset by 36.53
    
    return temp



def get_upside(ax, ay, az):
    # Determine which side of the dice is up based on the accelerometer values
    threshold = 25000  # Adjust based on your experiment

    if ax > threshold:
        return 1  # Side 1 is up (X positive)
    elif ax < -threshold:
        return 2  # Side 2 is up (X negative)
    elif ay > threshold:
        return 3  # Side 3 is up (Y positive)
    elif ay < -threshold:
        return 4  # Side 4 is up (Y negative)
    elif az > threshold:
        return 5  # Side 5 is up (Z positive)
    else:
        return 6  # Side 6 is up (Z negative)

def update_led(side):
    # Change LED color based on the current side
    if side in colors:
        for i in range(len(strip)):  # Loop through all LEDs in the strip
            strip[i] = colors[side]
        strip.show()  # Update the strip with the new color values
        print(f"Side {side} is up, LED color changed to {colors[side]}")



def update_pwm(side):
    # Change PWM brightness based on the current side (optional)
    duty_cycle = side * 20  # Set brightness based on side (1=20%, 6=120%)
    duty_cycle = max(0, min(100, duty_cycle))
    print(f"Calculated duty cycle: {duty_cycle}")
    pwm.ChangeDutyCycle(duty_cycle)

def main():
    try:
        while True:
            # Read the sensor data
            x, y, z = read_gyro()
            ax, ay, az = read_accel()
            temp = read_temp()
            
            # Print the sensor data
            print(f"Gyro: X={x}, Y={y}, Z={z}")
            print(f"Accel: X={ax}, Y={ay}, Z={az}")
            print(f"Temperature: {temp:.2f}°C")

            # Determine which side of the cube is facing up
            side = get_upside(ax, ay, az)
            print(f"Side {side} is up.")

            # Update the LED color and PWM based on the side
            update_led(side)
            update_pwm(side)

            # Wait for a short period before reading again
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Program interrupted.")
    finally:
        pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
