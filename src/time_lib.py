import machine
from time import *
import utime
import usocket as socket
import ustruct as struct
import gc

#GMT_OFFSET = 3600 * 1 # 3600 = 1 h (Winterzeit)
#GMT_OFFSET = 3600 * 2 # 3600 = 1 h (Sommerzeit)
GMT_OFFSET = 0
NTP_HOST = 'pool.ntp.org'
NTP_DELTA = 2208988800

msg_cooldown_timestamp = 0
btn_cooldown_timestamp = 0

def doWait(delay):
    utime.sleep(delay)

def getTimeNTP():
    try:
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1B
        addr = socket.getaddrinfo(NTP_HOST, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.settimeout(1)
            res = s.sendto(NTP_QUERY, addr)
            msg = s.recv(48)
        finally:
            s.close()
        ntp_time = struct.unpack("!I", msg[40:44])[0]
        print(f'unformated ntp: {ntp_time}')
        return utime.gmtime(ntp_time - NTP_DELTA + GMT_OFFSET)
    except Exception as e:
        if isinstance(e, OSError) and s: # If the error is an OSError the socket has to be closed.
            s.close()
            gc.collect()
        return False

def setTimeRTC():
    # NTP-Zeit holen
    tm = getTimeNTP()
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))

def getTimeRTC():
    #print("get RTC time")
    rtc = machine.RTC()
    return rtc.datetime()

def getUnixTimeRTC():
    tm = getTimeRTC()
    tmr = (tm[0], tm[1], tm[2], tm[4], tm[5], tm[6], tm[3], 0)
    return utime.mktime(tmr)

def setMsgCooldown(delay):
    global msg_cooldown_timestamp
    msg_cooldown_timestamp = getUnixTimeRTC() + (delay*60)

def getMsgCooldownStatus():
    try:
        if getUnixTimeRTC() > msg_cooldown_timestamp:
            #print("no cooldown")
            return True
        else:
            print(f'{msg_cooldown_timestamp-getUnixTimeRTC()} seconds remaining on cooldown')
            return False
    except Exception as e:
        print(f'Something went wrong in getCooldownStatus {e}')

    return False

def setBtnCooldown(delay):
    global btn_cooldown_timestamp
    btn_cooldown_timestamp = getUnixTimeRTC() + (delay*60)

def getBtnCooldownStatus():
    try:
        if getUnixTimeRTC() > btn_cooldown_timestamp:
            #print("no cooldown")
            return True
        else:
            print(f'{btn_cooldown_timestamp-getUnixTimeRTC()} seconds remaining on button cooldown')
            return False
    except Exception as e:
        print(f'Something went wrong in getCooldownStatus {e}')

    return False

def zeroPad(num):
    if num < 10:
        return f'0{num}'
    else:
        return f'{num}'

def getDatetimeString(timeStr):
    #print(f'getTimeString {timeStr}')

    if timeStr == (0,0,0,0,0,0,0,0):
        return ""
    return f'(last updated {timeStr[4]}:{timeStr[5]} GMT, {zeroPad(timeStr[2])}.{zeroPad(timeStr[1])})'

def getTimeString(timeStr):
    if timeStr == (0,0,0,0,0,0,0,0):
        return ""
    current_time = getUnixTimeRTC()
    tmr = (timeStr[0], timeStr[1], timeStr[2], timeStr[4], timeStr[5], timeStr[6], timeStr[3], 0)
    diff = int((current_time - utime.mktime(tmr))/3600)
    return f'(last updated {diff} hours ago)'

def doSleep(delaySeconds):
    time.sleep(delaySeconds)
