'''
09/04/2019
Single MPU9250 connected to Raspberry Pi 3 A+ or Zero through I2C
Setup: install python-smbus and i2c-tools
Run: sudo python3 MPU9250.py > result.log

IMU unit desired settings:
    - AXL "Low NOISE Mode" enabled (draws more current)
    - AXL full scale range: AFS_SEL = 01 (+/-4g):           Register 28: [4:3]
    - AXL output data rate 1kHz
    - AXL low pass filter to max value of 260 Hz
    - GYRO full scale range: FS_SEL = 00:                   Register 27: [4:3] = 00 by default
    - GYRO output data rate 1kHz
    - GYRO lowpass filter to max value of 250 Hz
    - Magnetometer: off (AXL + GYRO only mode)
    - I2C speed: Fast Mode 400kHz:                          Register 36 I2C Master Control [3:0]
                                                            sudo nano /boot/config.txt
                                                            Add this line to the file: dtparam=i2c_arm=on,i2c_baudrate=400000
'''



# ---------------------------------------------------------------------------------- #

import smbus
import time


# Global Variables:
OUTPUT_FREQ         = 1         # The output frequency. Ideal freq should be 1000 Hz.
MPU_ADDR            = 0x68      # The I2C address of the IMU unit. Use 'i2cdetect -y 1'.
MPU_ADDR2           = 0x69
WHO_AM_I            = 0x75
WHO_AM_I_DEFAULT    = 0x71
# Data Registers:
ACCEL_XOUT_H        = 0x3B
GYRO_XOUT_H         = 0x43
TEMP_OUT_H          = 0x41
TEMP_OUT_L          = 0x42
# Configuration Registers:
H_RESET_BIT         = 0x80
PWR_MGMT_1          = 0x6B
GYRO_CONFIG         = 0x1B
GYRO_FS_SEL_00      = 0x00      # unused because reset default value is 0x00
ACCEL_CONFIG        = 0x1C
AFS_SEL_01          = 0x08
I2C_MST_CTRL        = 0x24
I2C_MST_CLK_400KHZ  = 0x0D
# Setup I2C bus
bus = smbus.SMBus(1)



# -------------------------------- Class Definition -------------------------------- #

class MPU_9250:

    # Constructor:
    def __init__(self, address):
        self.address = address
        self.gyro_raw = [0, 0, 0, 0, 0, 0]
        self.accel_raw = [0, 0, 0, 0, 0, 0]
        self.gyro_x = self.gyro_y = self.gyro_z = 0.0
        self.accel_x = self.accel_y = self.accel_z = 0.0
        self.gfs = 250 / 32768          # Gyro Full Scale 250dps
        self.afs = 4 / 32768          # Accel Full Scale 4g
        self.temperature = 0


    # Setup the desired IMU unit settings for Garfield by writing to configuration registers
    def setup(self):
        bus.write_byte_data(self.address, PWR_MGMT_1, H_RESET_BIT)             # Reset first
        bus.write_byte_data(self.address, ACCEL_CONFIG, AFS_SEL_01)            # AXL full scale range: AFS_SEL = 01
        bus.write_byte_data(self.address, I2C_MST_CTRL, I2C_MST_CLK_400KHZ)    # I2C Fast Mode 400kHz

        '''
        bus.write_byte_data(self.address, 0x1A, 0x03)           # not sure
        bus.write_byte_data(self.address, 0x19, 0x04)           # not sure
        bus.write_byte_data(self.address, ACCEL_CONFIG2, 0x03)  # not sure
        To-do list: (Hard / not in datasheet)
        AXL "Low Noise Mode" enabled (draws more current) [NOT LOW POWER MODE]
        AXL output data rate 1kHz GYRO output data rate 1kHz
        AXL low pass filter to max value of 260 Hz
        GYRO low pass filter to max value of 250 Hz
        Magnetometer: off (AXL + GYRO only mode)
        '''
        return


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
        # Convert from 2's complement then to Accel / Gyro full scale
        self.accel_x = self.convert(self.accel_x) * self.afs
        self.accel_y = self.convert(self.accel_y) * self.afs
        self.accel_z = self.convert(self.accel_z) * self.afs
        self.gyro_x = self.convert(self.gyro_x) * self.gfs
        self.gyro_y = self.convert(self.gyro_y) * self.gfs
        self.gyro_z = self.convert(self.gyro_z) * self.gfs


    def convert(self, data):
        data = (data - 2 ** 16) if (data >= 2 ** 15) else data
        return data


    # Print format: timestamp, accel x, y, z, gyro x, y, z for IMU unit
    def output(self):
        print("%.4f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f" % (time.time(), self.accel_x, self.accel_y, self.accel_z, self.gyro_x, self.gyro_y, self.gyro_z))


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



# -------------------------------- Start of Main function -------------------------------- #

def main():
    sensor = MPU_9250(MPU_ADDR)
    sensor.test_connection()
    sensor.setup()
    while True:
        sensor.update()
        sensor.output()
        time.sleep(1 / OUTPUT_FREQ)


if __name__ == '__main__':
    main()
