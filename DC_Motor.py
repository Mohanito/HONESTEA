BOARD_PWM = 32
BOARD_STANDBY = 11
BOARD_IN1 = 18
BOARD_IN2 = 22


import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BOARD)
GPIO.setup(BOARD_PWM, GPIO.OUT)
pwm = GPIO.PWM(BOARD_PWM, 3)
pwm.start(50)   #duty cycle
GPIO.setup(BOARD_STANDBY, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(BOARD_IN1, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(BOARD_IN2, GPIO.OUT, initial = GPIO.LOW)

#initialize to Stop mode
GPIO.output(BOARD_IN1, GPIO.LOW)
GPIO.output(BOARD_IN2, GPIO.LOW)
#GPIO.output(BOARD_PWM, GPIO.HIGH)
GPIO.output(BOARD_STANDBY, GPIO.HIGH)

for i in range(6):
    if i % 2 == 0:
        #run cw
        print("motor running clockwise...")
        GPIO.output(BOARD_IN1, GPIO.HIGH)
        GPIO.output(BOARD_IN2, GPIO.LOW)
        #GPIO.output(BOARD_STANDBY, GPIO.HIGH)   #unnecessary
        time.sleep(2)
    else:
        #run ccw
        print("motor running counterclockwise...")
        GPIO.output(BOARD_IN1, GPIO.LOW)
        GPIO.output(BOARD_IN2, GPIO.HIGH)
        time.sleep(2)

#must reach this step to exit normally
print("cleaning up...")
GPIO.cleanup()  #works but needs to work with the infinite loop