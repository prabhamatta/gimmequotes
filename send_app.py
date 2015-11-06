from time import time, sleep
import json
import csv
from run import send_sms

USER_DATA_FILE = 'users_data.json'
MESSAGES_INFO_FILE = 'msgs_info.json'
SENT_MESSAGES_LOG_FILE = 'sent_msgs.log'
all_quotes = []
NUM_QUOTES = 100000

MAIN_LOOP_SLEEP_TIME = 2  # in seconds
USER_FREQ_UNIT = 60  # in seconds

def is_time_to_send_message(t1, t2, freq):
    secs = freq * USER_FREQ_UNIT
    if t1 - t2 > secs:
        return True
    return False

def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as udfile:
            udata = udfile.read()
    except:
        print "Error in reading file : %s" % USER_DATA_FILE
        udata = "{}"
    return json.loads(udata)

def load_last_messages_info():
    try:
        with open(MESSAGES_INFO_FILE, 'r') as mtfile:
            msgs_info = mtfile.read()
    except:
        msgs_info = {}
        with open(MESSAGES_INFO_FILE, 'w') as mtfile:
            msgs_info = json.dumps(msgs_info)
            mtfile.write(msgs_info)
    return json.loads(msgs_info)

def save_last_messages_info(msgs_info):
    try:
        with open(MESSAGES_INFO_FILE, 'w') as mtfile:
            mtfile.write(json.dumps(msgs_info))
    except:
        print "Error in writing file : %s" % MESSAGES_INFO_FILE

def log_sent_messages(messages_log):
    with open(SENT_MESSAGES_LOG_FILE, 'ab') as smfile:
        flwriter = csv.writer(
                smfile,
                delimiter=',',
                quoting=csv.QUOTE_MINIMAL,
                lineterminator='\n',
                )
        for msg in messages_log:
            flwriter.writerow(msg)

def get_last_msg_index_and_time(number, msgs_data):
    msg_time, msg_index, msg_count = msgs_data.get(number, (0, 0, 0))

    if msg_time == 0:
        from random import randint
        msg_index = randint(0, NUM_QUOTES - 1)
    return msg_time, msg_index, msg_count

def send_message(number, msg_index):
    msg = all_quotes[msg_index % NUM_QUOTES]
    msg = "%s\n    - %s" % (msg[1], msg[0])
    print "*"*60
    print "Sending message\n%s\nto number : %s\n" % (msg, number)
    send_sms(number , msg)

def run_periodically():
    """
    This function is called every MAIN_LOOP_SLEEP_TIME seconds
    to send messages to subscribed numbers
    """
    last_messages_info = load_last_messages_info()
    messages_log = []
    now = int(time())

    udata = load_user_data()
    for number, data in udata.items():
        freq = int(data['frequency'])
        if data['event_request'] == 'SUBSCRIBE':
            last_msg_time, last_msg_index, last_msg_count = \
                    get_last_msg_index_and_time(number, last_messages_info)
            if is_time_to_send_message(now,
                                       last_msg_time,
                                       freq):

                send_message(number, last_msg_index + 1)
                last_messages_info[number] = (now, last_msg_index + 1, last_msg_count + 1)
                messages_log.append([number, now, last_msg_index])

    save_last_messages_info(last_messages_info)
    log_sent_messages(messages_log)

def load_quotes():
    global all_quotes
    global NUM_QUOTES
    with open('quotes.json', 'r') as quotes_json:
        all_quotes = json.loads(quotes_json.read())
        NUM_QUOTES = len(all_quotes)

def main():
    load_quotes()
    while True:
        run_periodically()
        sleep(MAIN_LOOP_SLEEP_TIME)

if __name__ == "__main__":
    main()
