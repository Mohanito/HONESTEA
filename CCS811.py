'''
Requirements: sudo pip3 install adafruit-circuitpython-ccs811
Once I2C is enabled, we need to slow the speed way down due to constraints of this particular sensor.
sudo nano /boot/config.txt
add this line to the file: dtparam=i2c_baudrate=10000
'''
import busio
import board
import time
import adafruit_ccs811

def main():
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_ccs811.CCS811(i2c_bus)
    while not sensor.data_ready:
        pass
    while True:
        print("CO2: ", sensor.eco2, "PPM   TVOC:", sensor.tvoc, " PPM")
        time.sleep(0.5)

if __name__ == '__main__':
    main()