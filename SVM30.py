import smbus
import time

# Global Variables
VOC_ADDR = 0x58

# Setup i2c Bus
bus = smbus.SMBus(1)

class SGP30:

    # Constructor:
    def __init__(self):
        self.file_output = open("VOC_output.csv", "w+")
        self.file_output.write("CO2eq, tVOC, start_time\n")
        self.CO2eq = -1
        self.tVOC = -1
        self.start_time = -1
        return

    # Sending an "Init_air_quality" command starts the air quality measurement.
    # For the first 15s after the "Init_air_quality" command, the sensor is in an initialization phase
    # during which a "Measure_air_quality" command returns fixed values of 400 ppm CO2eq and 0 ppb tVOC.
    def init_measure(self):
        print("The sensor is in initialization phase... Please wait 15 seconds.")
        print("Default output: CO2eq = 400 ppm  and 0 ppb tVOC.")
        self.start_time = time.time()
        bus.write_byte_data(VOC_ADDR, 0x20, 0x03)
        #time.sleep(15)
        return

    # After init_measure, a "Measure_air_quality" command has to be sent in regular intervals of 1s to ensure proper operation.
    # 1st - 6th byte: (CO2eq MSB + LSB) - CRC - (tVOC MSB + LSB) - CRC
    def measure(self):
        bus.write_byte_data(VOC_ADDR, 0x20, 0x08)
        time.sleep(0.1)
        data = bus.read_i2c_block_data(VOC_ADDR, 0, 6)
        self.CO2eq = data[0] * 256 + data[1]
        self.tVOC = data[3] * 256 + data[4]
        print("-----------------------------------")
        print("CO2eq: " + str(self.CO2eq) + " (ppm)")
        print("tVOC:  " + str(self.tVOC) + " (ppd)")
        print("Sensor Running Time: %.2f seconds." % (time.time() - self.start_time))
        time.sleep(0.9)
        return

    def csv_write(self):
        self.file_output.write("%d, %d, %.2f\n" % (self.CO2eq, self.tVOC, time.time() - self.start_time))

def main():
    sensor = SGP30()
    sensor.init_measure()
    for i in range(45 + 15):
        sensor.measure()
        sensor.csv_write()
    sensor.file_output.close()
    bus.close()

if __name__ == '__main__':
    main()