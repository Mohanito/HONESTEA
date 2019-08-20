'''
08/07/2019
TCS3471 Color Light-to-digital Converter to Raspberry Pi 3 A+
Installed i2c-tools & python-smbus on Raspbian
Needs further research on calculating luminance & classifying colors
Useful commands: i2cdetect -y 1 (0 for old version of Raspberry Pi)
                i2cdetect -F 1
'''

import smbus
import time

# TCS3471 Registers (0x01 - 0x13 are unused. See datasheet)
ENABLE = 0x00
# RGBC Channel Data Registers
CLEAR_LOW = 0x14
CLEAR_HIGH = 0x15
RED_LOW = 0x16
RED_HIGH = 0x17
GREEN_LOW = 0x18
GREEN_HIGH = 0x19
BLUE_LOW = 0x1A
BLUE_HIGH = 0x1B
COLOR_REG_LIST = ["CLEAR_LOW", "CLEAR_HIGH", "RED_LOW", "RED_HIGH",
                  "GREEN_LOW", "GREEN_HIGH", "BLUE_LOW", "BLUE_HIGH"]

# Global Variables
COMMAND_BIT = 0b10000000
TCS3471_ADDR = 0x39

# Setup i2c Bus
bus = smbus.SMBus(1)


class TCS3471:
    
    # Constructor:
    # Setup ENABLE Register (Commented out)
    # Initialize class variables:
    #    color_data list: C_LOW, C_HIGH, R_LOW, R_HIGH, G_LOW, G_HIGH, B_LOW, B_HIGH for index 0 - 7
    #    luminance list: Clear, Red, Green, Blue, Ambient
    def __init__(self):
        '''
        bus.write_byte(address, 0b10000000)
        bus.write_byte(address, 0b00011011)
        '''
        self.color_data = [0, 0, 0, 0, 0, 0, 0, 0]
        self.luminance = [0, 0, 0, 0, 0]
    
    
    # read_reg: Write to COMMAND register first to specify the register address to R/W, then read.
    # param: register address
    # return value: 1 byte read from the register through i2c bus.
    def read_reg(self, reg_addr):
        bus.write_byte(TCS3471_ADDR, COMMAND_BIT | reg_addr)
        return bus.read_byte(TCS3471_ADDR)
    
    
    # display_regs: Output RGBC Channel Data Registers (0x14 - 0x1B) to screen
    # param: none, return value: none
    def display_regs(self):
        for reg_addr in range(CLEAR_LOW, BLUE_HIGH + 1):
            bus.write_byte(TCS3471_ADDR, COMMAND_BIT | reg_addr)
            self.color_data[reg_addr - CLEAR_LOW] = self.read_reg(reg_addr)
            print(COLOR_REG_LIST[reg_addr - CLEAR_LOW] + " = " + str(self.color_data[reg_addr - CLEAR_LOW]))


    # calculate_luminance: Clear, red, green, and blue data is stored as 16-bit values (2 bytes) in TCS3471.
    #                      Therefore, the 16-bit value = upper byte * 256 + lower byte.
    #                      Also calculates Ambient Data Color Luminance.
    # param: none, return value: none
    def calculate_luminance(self):
        for i in range(len(self.luminance) - 1):
            self.luminance[i] = self.color_data[i * 2 + 1] * 256 + self.color_data[i * 2]
        # unsure about the formula from internet
        self.luminance[-1] = (-0.32466 * self.luminance[1] + (1.57837 * self.luminance[2]) + (-0.73191 * self.luminance[3]))
    
    
    def display_luminance(self):
        print("Clear Data Color Luminance = " + str(self.luminance[0]) + " lux")
        print("Red Data Color Luminance = " + str(self.luminance[1]) + " lux")
        print("Green Data Color Luminance = " + str(self.luminance[2]) + " lux")
        print("Blue Data Color Luminance = " + str(self.luminance[3]) + " lux")
        print("Ambient Data Color Luminance = " + str(self.luminance[4]) + " lux")
        
        
        
def main():
    sensor = TCS3471()
    while True:
        time.sleep(2)
        print("\n\nRunning in 0.5 Hz...")
        print("-----------------------------------")
        sensor.display_regs()
        print("-----------------------------------")
        sensor.calculate_luminance()
        sensor.display_luminance()
        print("-----------------------------------")
        

if __name__ == '__main__':
    main()
    
