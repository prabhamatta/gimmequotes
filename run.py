from flask import Flask, request, send_from_directory
from twilio.rest import TwilioRestClient
import twilio.twiml
import json
import time
from settings import *
from contextlib import contextmanager
import csv

PRODUCTION = True

BAD_REQUEST = "Sorry... we did not understand the request. Acceptable requests: \
'Subscribe K' - subscibe to a quote every K minutes, or 'Terminate' - to unsubscribe"
NEW_SUBS_MSG = "Welcome to GimmeQuotes. Your subscription was successful. You will \
receive a quote every %s minutes."
CHANGE_FREQ_MSG = "Your subscription was modified. You will \
now receive a quote every %s minutes."
SUBSCRIBE_AGAIN_MSG = "We are glad to see you back. You will \
receive a quote every %s minutes."
NEVER_SUBS = "Unsubscribe not required. Could not find a subscription for your number."
UNSUBS_MSG = "Successfully Unsubscribed. We are sad to see you go. You can always \
subscribe again by sending 'Subscribe K' to %s"
ALREADY_UNSUBS = "Your number is already unsubscribed. You will not receive any more \
quotes."

app = Flask("runtwilio")
client = TwilioRestClient(account=twilio_account_sid, token=twilio_auth_token)

@app.route('/images/<path:path>')
def send_from_images(path):
    return send_from_directory('images', path)


@app.route(incoming_mesgs_url, methods=['Post'])
def read_incoming_sms():
    number, msg, freq, body = get_request_info(request.form)

    if msg is None:
        print "Could not decipher a valid request"
        if number in (None, ""):
            return "Could not get the phone number from message"
        else:
            log_activity(number, "BAD_REQUEST", "-", body)
            return send_sms(number, BAD_REQUEST)

    if msg == 'SUBSCRIBE':
        log_activity(number, msg, freq, body)
        return subscribe_user(number, msg, freq, body)
    elif msg == 'TERMINATE':
        log_activity(number, msg, "-", body)
        return unsubscribe_user(number, msg, freq, body)

    log_activity(number, msg, "-", body)
    return send_sms(number, BAD_REQUEST)


@app.route("/", methods=['GET'])
def show_stats():
    return get_stats_result()


def log_activity(number, msg, freq, body):
    with open('user_activity.log', 'ab') as logfile:
        flwriter = csv.writer(
                logfile,
                delimiter=',',
                quoting=csv.QUOTE_MINIMAL,
                lineterminator='\n',
                )
        flwriter.writerow([number, msg, freq, body, time.time()])


def get_status(users_data, number):
    status = users_data.get(number, {}).get('event_request', "???")
    status_map = {
        "SUBSCRIBE": "Subscribed",
        "TERMINATE": 'Unsubscribed',
    }
    return status_map.get(status, '???')


def send_sms(number, msg):
    """
    Send an sms message to a given number
    Really sends the message if PRODUCTION is True... else only prints that
    its sending, without actually doing it.
    """
    if PRODUCTION is True:
        message = client.messages.create(to=number, from_=twilio_number, body=msg)
    else:
        print "*"*60
        print "Dummy sending sms to: %s\n%s\n" % (number, msg)
    return "Message Sent to Client"

def hide_number(number):
    return "..." + number[-4:]

def get_request_info(form):
    """
    Returns number, message and freq from an incoming message.
    """
    number, msg, freq = None, None, None
    body = str(form.get('Body', ""))
    try:
        number = form.get('From', "")
        msg_body = body.strip().split(" ")

        if len(msg_body) == 2:
            if msg_body[0].upper() == "SUBSCRIBE":
                msg = "SUBSCRIBE"
                freq = int(msg_body[1])
                assert freq > 0
        elif len(msg_body) == 1:
            if msg_body[0].upper() == "TERMINATE":
                msg = "TERMINATE"
                freq = 60
    except:
        try:
            number = form.get('From', None)
        except:
            number = None
        msg, freq = None, None
    return (number, msg, freq, body)


def subscribe_user(number, msg, freq, body):
    users_data = read_users_data()
    if number in users_data:
        user_info = users_data[number]
        if user_info['event_request'] == 'SUBSCRIBE':
            REPLY_MSG = CHANGE_FREQ_MSG % freq
        else:
            REPLY_MSG = SUBSCRIBE_AGAIN_MSG % freq
    else:
        REPLY_MSG = NEW_SUBS_MSG % freq
    send_sms(number, REPLY_MSG)
    update_users_data(number, msg, freq, body, users_data)
    return "Subscription successful"


def unsubscribe_user(number, msg, freq, body):
    users_data = read_users_data()
    if number in users_data:
        user_info = users_data[number]
        if user_info['event_request'] == 'SUBSCRIBE':
            REPLY_MSG = UNSUBS_MSG % GIMME_QUOTES_NUMBER
        else:
            REPLY_MSG = ALREADY_UNSUBS
    else:
        send_sms(number, NEVER_SUBS)
        # don't store data for a number which never subscribed.
        return "Unsubscribe not applicable"

    send_sms(number, REPLY_MSG)
    update_users_data(number, msg, freq, body, users_data)
    return "Unsubscribe successful"


def read_users_data():
    try:
        with open('users_data.json', 'r') as ufile:
            users_data = json.loads(ufile.read())
    except:
        users_data = {}
    return users_data


def update_users_data(number, msg, freq, body, users_data=None):
    curr_userid = number
    curr_user_data = {}
    curr_user_data['event_request'] = msg
    curr_user_data['frequency'] = freq
    curr_user_data['mesg'] = body
    curr_user_data['timestamp'] = time.time()

    if users_data is None:
        users_data = read_users_data()

    users_data[curr_userid] = curr_user_data

    with open('users_data.json', 'w') as f:
        f.write(json.dumps(users_data))
        f.close()
    return


stats_html_content = """
<html>
  <style>
    body {{
      font-size: x-small;
      margin-bottom: 50px;
    }}
    table, th, td {{
      border: 1px solid #888;
      border-collapse: collapse;
      font-size: 12px;
    }}
    th, td {{
      padding: 5px;
      text-align: left;
    }}
    #container {{
      margin-right: auto;
      margin-left: auto;
      width: 800px;
    }}
    header {{
      margin-right: auto;
      margin-left: auto;
      margin-top: 20px;
      width: 800px;
    }}
    .centerImage {{
      margin-left: auto;
      margin-right: auto;
      display: block;
    }}
    #instructions{{
        font-size: 30px;
        margin: 5px;
        font-weight: bold;
    }}
    #subinstructions{{
        margin: 5px;
        text-align: right;
    }}
  </style>
<body>
  <header>
    <img class='centerImage' src="images/gimmequotes.png"/>
  </header>
  <div id="container">
    <div id="instructions">
        Welcome to GimmeQuotes...
        <div id="subinstructions">
            <table style="width: 100%; border: None;">
            <tr>
            <td style="width: 100%; border: None; font-size: 14px;"></td>
            <td style="white-space: nowrap; border: None; font-size: 14px;">
                <p> send 'Subscribe 2' to 6502295612 to receive a quote every 2 minutes </p>
                <p> To modify subscription, send 'Subscribe 5' to 6502295612 to receive a quote every 5 minutes </p>
                <p> send 'Terminate' to 6502295612 to unsubscribe </p>
             </td>
             </tr>
            </table>
        </div>
    </div>
    <div>
      <h1>User Status</h1>
      {table_users}
    </div>

    <div>
        <br/><br/>
      <h1>User activity log (most recent 10)</h1>
      {table_user_activity_log}
    </div>

    <div>
        <br/><br/>
      <h1>Message log (most recent 10)</h1>
      {table_sent_messages}
    </div>

    <div style="width: 100%; text-align:center; font-size: 14px;">
        <br/>
        <hr/>
        <br/>
        <br/>
        <p>&copy; Prabhavathi Matta</p>
      </div>
  </div>
</body>
</html>
"""

def get_stats_result():
    msgs_data = json.loads(open('msgs_info.json').read())
    users_data = json.loads(open('users_data.json').read())

    users_table = "<table>\n"
    users_table += "  <tr>\n"
    for th in ["Phone Number", "Sub status", "Frequency", "# Messages"]:
        users_table += "    <th>%s</th>\n" % th
    users_table += "  </tr>\n"
    for number, usr_info in users_data.items():
        users_table += "  <tr>\n"
        new_number = hide_number(number)
        info = msgs_data.get(number, ['?']*3)
        for td in [new_number, get_status(users_data, number),
                   usr_info.get('frequency', '???'), info[2]]:

            users_table += "    <td>%s</td>\n" % td
        users_table += "  </tr>\n"
    users_table += "</table>\n"

    sent_msgs_table = "<table>"
    sent_msgs_table += "  <tr>\n"
    for th in ["Phone Number", "Time", "Quote Index"]:
        sent_msgs_table += "    <th>%s</th>\n" % th
    sent_msgs_table += "  </tr>\n"
    with open('sent_msgs.log', 'r') as sm:
        reader = csv.reader(sm)
        for row in reversed(list(reader)[-10:]):
            number, tm, index = row
            ctm = time.ctime(float(tm))
            new_number = hide_number(number)
            sent_msgs_table += "  <tr>\n"
            for td in [new_number, ctm, index]:
                sent_msgs_table += "    <td>%s</td>\n" % td
            sent_msgs_table += "  </tr>\n"
    sent_msgs_table += "</table>"

    user_activity_table = "<table>"
    user_activity_table += "  <tr>\n"
    for th in ["Phone Number", "Request", "Frequency", "Message Body", "Time"]:
        user_activity_table += "    <th>%s</th>\n" % th
    user_activity_table += "  </tr>\n"
    with open('user_activity.log', 'r') as ua:
        reader = csv.reader(ua)
        for row in reversed(list(reader)[-10:]):
            number, msg, freq, body, tm = row
            number = hide_number(number)
            ctm = time.ctime(float(tm))
            user_activity_table += "  <tr>\n"
            for dt in [number, msg, freq, body, ctm]:
                user_activity_table += "    <td>%s</td>\n" % dt
            user_activity_table += "  </tr>\n"
    user_activity_table += "</table>"


    return stats_html_content.format(table_users=users_table,
                                     table_sent_messages=sent_msgs_table,
                                     table_user_activity_log=user_activity_table)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8000)
