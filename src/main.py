# Ideas:
# admin command /debug that returns cooldown status, system time etc.

from machine import Pin
from network_lib import *
from secrets import *
from time_lib import *
from messages import *
import re
import os

from machine import WDT


# Constants
msgCooldownPeriod = 30
btnCooldownPeriod = 15
minParseLen = 5
maxParseLen = 120

# Global Variables
basementStatus = False
basementStatusOld = False
ignore = False
last_changed = (0,0,0,0,0,0,0,0)

def set_last_changed():
    global last_changed
    last_changed = getTimeRTC()
    file = open("last_change.txt", 'w')
    file.write(str(last_changed))
    file.close()

def get_last_changed_file():
    global last_changed
    file = open("last_change.txt", 'r')
    last_changed = eval(file.read())
    file.close()



def set_ignore(val):
    global ignore
    file = open('status.txt', 'w')
    if val:
        file.write("1")
    else:
        file.write("0")
    ignore = val
    file.close()

def get_ignore():
    file = open('status.txt', 'r')
    ret_val = file.read()
    file.close()
    if ret_val == '1':
        return True
    else:
        return False

def check_combinations(message):
    reg1 = ".*(keller|basement|endstation|community room|bar).* (open|closed|offen|geöffnet|geschlossen).*\?"
    return (re.search(reg1, message) != None)


def announce_status(status, pre_str, post_str, chat_id):
    if pre_str == "":
        pre_str = "The community room \"Endstation\" is now"

    if status:
        send_message(chat_id, f'{pre_str} open. {post_str}')
    else:
        send_message(chat_id, f'{pre_str} closed. {post_str}')


def handle_message(chat_id, date, message):
    global basementStatus, last_changed
    try:
        # Empty message
        if (len(message) < minParseLen) or (len(message) > maxParseLen):
            return False

        # Avoid handling old messages after bot startup
        if date != False:
            diff = getUnixTimeRTC() - date - GMT_OFFSET
            print(f'frame time diff: {diff}')
            if diff > 30:
                return False

        if message.startswith("@endstationbot"):
            EndstationMessage = True
        else:
            EndstationMessage = False

        print(f'User ({chat_id}): "{message}"')
        if ("forceclose" in message) and EndstationMessage:
            if chat_id == secrets['admin']:
                print("force status closed")
                basementStatus = False
                if ignore == False:
                    set_ignore(True)

        elif ("forceopen" in message) and EndstationMessage:
            if chat_id == secrets['admin']:
                print("force status open")
                basementStatus = True
                if ignore == False:
                    set_ignore(True)

        elif ("help" in message) and EndstationMessage:
            if chat_id == secrets['admin']:
                send_message(chat_id, help_message)
                basementStatus = False
                return False

        else: # General Commands
            # WH Group messages cooldown to avoid spam
            if (not getMsgCooldownStatus()) and (chat_id == secrets['WHGroupIDint']):
                return False

            if ((("basementstatus" in message) and EndstationMessage) or check_combinations(message)):
                announce_status(basementStatus, f'The community room \"Endstation\" is currently', getTimeString(last_changed), chat_id)
                if chat_id == secrets['WHGroupIDint']:
                    setMsgCooldown(msgCooldownPeriod)

            if ("basementinfo" in message) and EndstationMessage:
                send_message(chat_id, baseinfo_message)
                if chat_id == secrets['WHGroupIDint']:
                    setMsgCooldown(msgCooldownPeriod)

        if basementStatusOld != basementStatus:
            set_last_changed()
        if "silent" in message:
            return False

        return basementStatusOld != basementStatus

    except Exception as e:
        print(f'something went wrong in handle_message {e}')

    return False


btn = Pin(28, Pin.IN, Pin.PULL_UP)

def getButtonStatus():
    global basementStatus, ignore, last_changed
    try:
        if ignore:
            if basementStatus == (not btn.value()):
                set_ignore(False)
            return

        if (basementStatus != (not btn.value())) and getBtnCooldownStatus():
            print("Button status changed")
            basementStatus = not btn.value()
            setBtnCooldown(btnCooldownPeriod)
            set_last_changed()

    except Exception as e:
        print(f'something went wrong in getButtonStatus {e}')

    return


# Main "Function"
led = Pin("LED", Pin.OUT)

led.off()
try:
    wdt = WDT(timeout=8300)  # enable watchdog with a timeout of 8s
    do_connect()

    wdt.feed()
    setTimeRTC()

    wdt.feed()
    if "status.txt" in os.listdir():
        ignore = get_ignore()
    else:
        set_ignore(False)


    wdt.feed()

    if "last_change.txt" in os.listdir():
        get_last_changed_file()

    if ignore:
        basementStatus = btn.value()
    else:
        basementStatus = not btn.value()

    print("Startup: ignore=" + str(ignore) + " basementStatus=" + str(basementStatus) + " last_changed=" + str(last_changed))
    wdt.feed()
except Exception as e:
    led.on()
    print("Resetting on startup...")
    doWait(5) # avoid frequent resets when no internet connection
    machine.reset()

#led.on()
while True:
    try:
        basementStatusOld = basementStatus
        wifi_poll_reconnect()
        wdt.feed()
        getButtonStatus()
        wdt.feed()
        if basementStatusOld != basementStatus:
            announce_status(basementStatus, "", "", secrets["WHGroupID"])
            wdt.feed()
            continue

        chat_id, date, message = read_message()
        wdt.feed()
        if handle_message(chat_id, date, message):
            wdt.feed()
            announce_status(basementStatus, "", "", secrets["WHGroupID"])

        wdt.feed()

    except Exception as e:
        led.on()
        print("Resetting...")
        doWait(5) # avoid frequent resets when no internet connection
        machine.reset()