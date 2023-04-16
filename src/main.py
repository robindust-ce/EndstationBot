# Ideen:
# admin command /setcooldown=<val> oder /invokecooldown

from machine import Pin
from network_lib import *
from secrets import *
from time_lib import *
from messages import *

basementStatus = False
basementStatusOld = False
ignore = False

last_changed = (0,0,0,0,0,0,0,0)

keller_list = ("keller", "basement", "endstation", "bar", "community room",)
open_list = ("offen", "open",)
def check_combinations(message):
    if "?" not in message:
        return False
    for i in keller_list:
        if i in message:
            for j in open_list:
                if j in message:
                    return True
    return False

def announce_status(status, pre_str, post_str, chat_id):
    if pre_str == "":
        pre_str = "The community room \"Endstation\" is now"

    if status:
        send_message(chat_id, f'{pre_str} open. {post_str}')
    else:
        send_message(chat_id, f'{pre_str} closed. {post_str}')


def handle_message(chat_id, date, message):
    global basementStatus, last_changed, ignore
    try:
        # Empty message
        if message == "":
            return False

        # Avoid handling old messages after bot startup
        if date != False:
            diff = getUnixTimeRTC() - date - GMT_OFFSET
            print(f'frame time diff: {diff}')
            if diff > 30:
                return False

        print(f'User ({chat_id}): "{message}"')
        if "/forceclose" in message:
            if chat_id == secrets['admin']:
                print("force status closed")
                basementStatus = False
                ignore = True

        elif "/forceopen" in message:
            if chat_id == secrets['admin']:
                print("force status open")
                basementStatus = True
                ignore = True
                
        elif "/help" in message:
            if chat_id == secrets['admin']:
                send_message(chat_id, help_message)
                basementStatus = False

        else: # General Commands
            if not getMsgCooldownStatus():
                return False

            if (("/basementstatus" in message) or check_combinations(message)):
                announce_status(basementStatus, f'The community room \"Endstation\" is currently', getTimeString(last_changed), chat_id)
                if chat_id == secrets['WHGroupIDint']:
                    setMsgCooldown(1)

            if ("/basementinfo" in message):
                send_message(chat_id, baseinfo_message)
                if chat_id == secrets['WHGroupIDint']:
                    setMsgCooldown(1)

        if basementStatusOld != basementStatus:
            last_changed = getTimeRTC()
        if "silent" in message:
            return False

        return basementStatusOld != basementStatus

    except Exception as e:
        print(f'something went wrong in handle_message {e}')

    return False


btn = Pin(28, Pin.IN, Pin.PULL_UP)

def getButtonStatus():
    global basementStatus, ignore
    try:
        if ignore:
            if basementStatus == (not btn.value()):
                ignore = False
            return
            
        if (basementStatus != (not btn.value())) and getBtnCooldownStatus():
            print("Button status changed")
            basementStatus = not btn.value()
            setBtnCooldown(3)

    except Exception as e:
        print(f'something went wrong in getButtonStatus {e}')

    return
    
led = Pin("LED", Pin.OUT)
led.off()
try:    
    do_connect()
    # led.on()
    #send_message(secrets['WHGroupID'], "Startup")
    setTimeRTC()
    basementStatus = not btn.value()
except Exception as e:
    print("Resetting on startup...")
    led.off()
    doWait(3) # avoid frequent resets when no internet connection
    machine.reset()
        
led.on()        
while True:
    try:
        basementStatusOld = basementStatus
        wifi_poll_reconnect()
        chat_id, date, message = read_message()
        getButtonStatus()
        if basementStatusOld != basementStatus:
            announce_status(basementStatus, "", "", secrets["WHGroupID"])
        if handle_message(chat_id, date, message):
            announce_status(basementStatus, "", "", secrets["WHGroupID"])


    except Exception as e:
        print("Resetting...")
        led.off()
        doWait(3) # avoid frequent resets when no internet connection
        machine.reset()