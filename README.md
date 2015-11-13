
## An SMS App using Twilio's api to periodically send quotes to subscribers
http://gimmequotes.info/

Step1: Create Twilio account and get the basic info
------
##### Create ‘settings.py’ file with following info:
```
twilio_account_sid = "<twilio account id>"
twilio_auth_token = "<twilio auth token>"
twilio_number = "<twilio ph number>"
incoming_mesgs_url = "<incoming mesg url>"

```

Step 2: Run the app that handles subscription and unsubscription
----------
* create virtual env
```
virtualenv venv
```
* activating virtual env
```
source env.sh
```
* install dependencies
```
pip install -r requirements.txt
```
* set
```
# for testing
PRODUCTION = false
# for running in production
PRODUCTION = True
```
* Now, run the application
```
python run.py

# To run in the background
nohup python run.py &
```

Step 3:  Run the app that handles periodic sending of quotes
---------
* go to the folder and run
```
source env.sh

# To run the application
python send_app.py

#To run in the background
nohup python send_app.py &
```
