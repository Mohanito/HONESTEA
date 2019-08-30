'''
8/30/2019
Single MPU9250 connected to Raspberry Pi 3 A+ or Zero through I2C
Setup: install python-smbus and i2c-tools
Run: sudo python3 MPU9250.py > result.log
'''
import smbus
import time

# Global Variable:
OUTPUT_FREQ         = 1         # The output frequency. Ideal freq should be 1000 Hz.
MPU_ADDR            = 0x68
MPU_ADDR2           = 0x69
WHO_AM_I            = 0x75
WHO_AM_I_DEFAULT    = 0x71
ACCEL_XOUT_H        = 0x3B
GYRO_XOUT_H         = 0x43
TEMP_OUT_H          = 0x41
TEMP_OUT_L          = 0x42
# Setup I2C bus
bus = smbus.SMBus(1)


class MPU_9250:
    def __init__(self, address):
        self.address = address
        self.gyro_raw = [0, 0, 0, 0, 0, 0]
        self.accel_raw = [0, 0, 0, 0, 0, 0]
        self.gyro_x = 0
        self.gyro_y = 0
        self.gyro_z = 0
        self.temperature = 0

    # Read raw data from register 0x3B - 0x40 for ACCEL, and 0x43 - 0x48 for GYRO.
    # Combine MSB and LSB of raw data on each direction, and then convert from 2's complement.
    def update(self):
        for i in range(6):
            self.accel_raw[i] = bus.read_byte_data(self.address, ACCEL_XOUT_H + i)
            self.gyro_raw[i] = bus.read_byte_data(self.address, GYRO_XOUT_H + i)
        # Combine MSB & LSB
        self.accel_x = (self.accel_raw[0] << 8) + self.accel_raw[1]
        self.accel_y = (self.accel_raw[2] << 8) + self.accel_raw[3]
        self.accel_z = (self.accel_raw[4] << 8) + self.accel_raw[5]
        self.gyro_x = (self.gyro_raw[0] << 8) + self.gyro_raw[1]
        self.gyro_y = (self.gyro_raw[2] << 8) + self.gyro_raw[3]
        self.gyro_z = (self.gyro_raw[4] << 8) + self.gyro_raw[5]
        # Convert from 2's complement
        self.accel_x = self.convert_2(self.accel_x)
        self.accel_y = self.convert_2(self.accel_y)
        self.accel_z = self.convert_2(self.accel_z)
        self.gyro_x = self.convert_2(self.gyro_x)
        self.gyro_y = self.convert_2(self.gyro_y)
        self.gyro_z = self.convert_2(self.gyro_z)

    def convert_2(self, data):
        data = (data - 2 ** 16) if (data >= 2 ** 15) else data
        return data

    # Print format: timestamp, accel x, y, z, gyro x, y, z for IMU unit
    def output(self):
        print("%.4f, %d, %d, %d, %d, %d, %d" % (time.time(), self.accel_x, self.accel_y, self.accel_z, self.gyro_x, self.gyro_y, self.gyro_z))

    # Check Device ID
    def test_connection(self):
        while not WHO_AM_I_DEFAULT == bus.read_byte_data(self.address, WHO_AM_I):
            print("Connection Failed! Please try again.")
            time.sleep(2)

    # Unused for Garfield project
    def get_temp(self):
        temp_msb = bus.read_byte_data(self.address, TEMP_OUT_H)
        temp_lsb = bus.read_byte_data(self.address, TEMP_OUT_L)
        temp_raw = (temp_msb << 8) + temp_lsb
        # self.temperature
        # TEMP_degC = ((TEMP_OUT - RoomTemp_Offset) / Temp_Sensitivity) + 21degC


def main():
    sensor = MPU_9250(MPU_ADDR)
    sensor.test_connection()
    while True:
        sensor.update()
        sensor.output()
        time.sleep(1 / OUTPUT_FREQ)

if __name__ == '__main__':
    main()
