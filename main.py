# -*- coding: utf-8 -*-

#############################################################
#                          IMPORTS                          #
#############################################################
from time import sleep

## Import all board pins.
import board
import busio
from digitalio import DigitalInOut, Direction

## Import PN532 RFID
from adafruit_pn532.spi import PN532_SPI

## PWM for buzzer
import simpleio

## Import the HT16K33 LED segment module.
from adafruit_ht16k33 import segments

## Import matrix keypad
import adafruit_matrixkeypad

#############################################################
#                          CONTENT                          #
#############################################################
COUNTER = 3
CODE = [1, 2, 3, 4]
MAX_CODE = 3
PASS_CARD = ['0x2', '0xa5', '0xa5', '0x35']

number_of_try = 1

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs_pin = DigitalInOut(board.D5)
pn532 = PN532_SPI(spi, cs_pin, debug=False)
pn532.SAM_configuration()

led = DigitalInOut(board.D53)
led.direction = Direction.OUTPUT
led.value = False

simpleio.tone(board.D11, 1000, duration=1)


## Classic 3x4 matrix keypad
cols = [DigitalInOut(x) for x in (board.D24, board.D22, board.D19, board.D18)]
rows = [DigitalInOut(x) for x in (board.D17, board.D16, board.D15, board.D14)]
keys = (( 1,  2,  3,  'A'),
        ( 4,  5,  6,  'B'),
        ( 7,  8,  9,  'C'),
        ('*', 0, '#', 'D'))

keypad = adafruit_matrixkeypad.Matrix_Keypad(rows, cols, keys)


## Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)
display = segments.Seg14x4(i2c)

##Clear the display.
display.fill(0)
sleep(0.1)

def end() :
    simpleio.tone(board.D11, 2000, duration=1)
    print("ID NOT VALID")
    display.marquee("ID NOT VALID    ",loop=False)
    display.marquee("SECURITY ALERTED    ",loop=False)

    i=0
    while i < 13 :
        simpleio.tone(board.D11, 2000, duration=0.5)
        sleep(0.5)
        i += 1
    number_of_try = 1

while True :
    display.marquee("READ ID CARD    ",loop=False)
    key_list = []
    uid = pn532.read_passive_target(timeout=0.5)
    if uid is None:
        continue
    card = [hex(i) for i in uid]
    print(card)
    if card == PASS_CARD:
        simpleio.tone(board.D11, 1000, duration=0.1)
        sleep(0.1)
        simpleio.tone(board.D11, 1000, duration=0.1)
        sleep(0.1)
        simpleio.tone(board.D11, 1000, duration=0.5)
        sleep(0.5)
        print("ID VALIDATED")
        display.marquee("ID VALIDATED    ",loop=False)
        
        display.marquee("ENTER CODE    ",loop=False)

        while len(key_list) <= 3 :
            keys = keypad.pressed_keys
            if keys:
                display.print(keys[0])
                key_list.append(keys[0])
                simpleio.tone(board.D11, 1000, duration=0.3)
                
            sleep(0.3)
            # print(key_list)

        if key_list == CODE :
            simpleio.tone(board.D11, 1000, duration=0.1)
            sleep(0.1)
            simpleio.tone(board.D11, 1000, duration=0.1)
            sleep(0.1)
            simpleio.tone(board.D11, 1000, duration=0.5)
            sleep(0.5)
            led.value = True
            display.marquee("FIAT LUX    ",loop=False)
            sleep(2)
            led.value = False

        else :
            if number_of_try < MAX_CODE :
                display.print("NOPE")
                simpleio.tone(board.D11, 2000, duration=2)
                display.print("WAIT")

                while COUNTER >= 1:
                    display.print(f"{COUNTER:04}")
                    simpleio.tone(board.D11, 1000, duration=0.5)
                    sleep(0.5)
                    COUNTER -= 1

                number_of_try += 1
                continue
            else :
                end()
    else :
        end()