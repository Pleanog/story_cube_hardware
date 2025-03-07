import smbus2
import time

# MPU-6050 Registers
MPU_ADDR = 0x68  # I2C address
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
TEMP_OUT_H = 0x41
GYRO_XOUT_H = 0x43

# Initialize I2C
bus = smbus2.SMBus(1)
bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)  # Wake up sensor

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

while True:
    ax, ay, az, temp, gx, gy, gz = read_sensor_data()
    face = determine_dice_face(ax, ay, az)

    print(f"Acceleration: X={ax:.2f}g, Y={ay:.2f}g, Z={az:.2f}g")
    print(f"Gyro: X={gx:.2f}°/s, Y={gy:.2f}°/s, Z={gz:.2f}°/s")
    print(f"Temperature: {temp:.2f}°C")
    print(f"Dice Face Up: {face}\n")
    print(f"-----------------------------------")

    time.sleep(1)
