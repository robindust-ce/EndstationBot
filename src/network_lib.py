import network
import time
from secrets import *
import gc
import urequests as requests

wlan = network.WLAN(network.STA_IF)
def do_connect(ssid=secrets['ssid'],psk=secrets['password']):
    wlan.active(True)
    wlan.connect(ssid, psk)

    # Wait for connect or fail
    wait = 10
    while wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('wifi connection failed')
        
    else:
        print('connected')
        ip=wlan.ifconfig()[0]
        print('network config: ', ip)
        return ip
    
def wifi_poll_reconnect():
    while not wlan.isconnected():
        do_connect()


sendURL = 'https://api.telegram.org/bot' + secrets['botToken'] + '/sendMessage'

# Send a telegram message to a given user id
def send_message (chatId, message):
    try:
        response = requests.post(sendURL + "?chat_id=" + str(chatId) + "&text=" + message + "&parse_mode=Markdown") #+ "&parse_mode=HTML"
        # Close to avoid filling up the RAM.
        response.close()
    except Exception as e:
        print(f'error in send_message {e}')


first_read = True
update_id = 0
def read_message():
    global first_read, update_id
    gc.collect()
    
    chat_id = False
    message = ""
    date = False

    get_url = 'https://api.telegram.org/bot' + secrets['botToken']
    get_url += "/getUpdates?limit=1&timeout=1&allowed_updates=[\"message\",\"callback_query\"]"
    if first_read == False:
        get_url += "&offset={}".format(update_id)
    print(f'try {get_url}')
    try:
        r = requests.get(get_url)
        print(f'got r {r.status_code}')
        response_json = r.json()
        print("got json")
        print(response_json)
        
        if len(response_json['result']) < 1 :
            return chat_id, date, message
        
        print("long enough")
        
        if "message" not in response_json['result'][0]:
            return chat_id, date, message
        
        print("is message")
        update_id = response_json['result'][0]['update_id']
        print(f'update id: {update_id}')
        if "text" in response_json['result'][0]['message']:
#             update_id = response_json['result'][0]['update_id']
            message = r.json()['result'][0]['message']['text'].lower()
            chat_id = r.json()['result'][0]['message']['chat']['id']
            date = r.json()['result'][0]['message']['date']

        first_read = False            
        update_id+=1
        print(f'update id + 1 {update_id}')
        
    except Exception as e:
        print(f'Exception {e} in read_message')
        if isinstance(e, OSError) and r: # If the error is an OSError the socket has to be closed.
            r.close()
        response_json = {"error": e}
    gc.collect()
    return chat_id, date, message    