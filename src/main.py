import paho.mqtt.client as mqtt
import evdev
import sys
from evdev import ecodes, InputDevice # , categorize

#============================
# Constants and Parameters
#============================

# MQTT parameters:
MQTT_IP = 'localhost'
QR_CODE_TOPIC = 'qrcode'

# Input for CAPS
CONST_CAPS_LSHFT = 42
CONST_CAPS_RSHFT = 54

# Input indicates end of barcode
CONST_ENTER = 28

CONST_KEY_DOWN = 1

scancodes = {0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8', 10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'q', 17: u'w', 18: u'e', 19: u'r', 20: u't', 21: u'y', 22: u'u', 23: u'i', 24: u'o', 25: u'p', 26: u'[', 27: u']', 28: u'CRLF', 29: u',', 30: u'a', 31: u's', 32: u'd', 33: u'f', 34: u'g', 35: u'h', 36: u'j', 37: u'k', 38: u'l', 39: u';', 40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'z', 45: u'x', 46: u'c', 47: u'v', 48: u'b', 49: u'n', 50: u'm', 51: u',', 52: u'.', 53: u'-', 54: u'RSHFT', 56: u'LALT', 57: u' ', 100: u'RALT'}

capscodes = {0: None, 1: u'ESC', 2: u'!', 3: u'"', 4: u'§', 5: u'$', 6: u'%', 7: u'&', 8: u'/', 9: u'(', 10: u')', 11: u'=', 12: u'_', 13: u'+', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R', 20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'{', 27: u'}', 28: u'CRLF', 29: u',', 30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u':', 40: u'\'', 41: u'~', 42: u'LSHFT', 43: u' ', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N', 50: u'M', 51: u'<', 52: u':', 53: u'?', 54: u'RSHFT', 56: u'LALT',  57: u' ', 100: u'RALT'}

#============================
# Help functions
#============================

# Callback function for connection to MQTT Client
def on_connect(client, userdata, flags, rc):
    print("Connected to " + MQTT_IP + " mqtt broker")

#============================
# Main Function 
#============================

# Initialize MQTT Client
client = mqtt.Client()
# Add callback functions
client.on_connect = on_connect
# Connect to databus
client.connect(MQTT_IP)
client.loop_start()

dev = InputDevice('/dev/input/event0')
barcode = ""
upper = 0


for event in dev.read_loop():
    
    if (event.type == evdev.ecodes.EV_KEY) and (event.value == CONST_KEY_DOWN):

        id = event.code

        # If the event.code means RSHFT oder LSHFT the next character will be caps:
        if event.code in [CONST_CAPS_LSHFT, CONST_CAPS_RSHFT]:
            upper = 1

        else:

            # Change letter to capitel letter (RSHFT/LSHFT before) -> character from capscodes-dictionary
            if upper == 1:
                value = capscodes[id]
                # CONST_ENTER indicates end of barcode and must be excluded:
                if event.code != CONST_ENTER:
                    barcode += value
                # Undo Caps for the next character:
                upper = 0

            # No RSHFT/LSHFT before -> character from scancodes-dictionary
            else:
                value = scancodes[id]
                # CONST_ENTER indicates end of barcode and must be excluded:
                if event.code != CONST_ENTER:
                    barcode += value

        # CONST_ENTER indicates end of barcode:
        if event.code == CONST_ENTER:
            print(barcode)

            # Publish barcode in MQTT Topic and flush to logs:
            client.publish(QR_CODE_TOPIC, barcode)

            sys.stdout.flush()
            # Reset barcode parameter:
            barcode = ""