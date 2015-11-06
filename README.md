Step1:
------
##### Create ‘settings.py’ file with following info:
```
twilio_account_sid = "<twilio account id>"
twilio_auth_token = "<twilio auth token>"
twilio_number = “<twilio ph number>"
```

Step 2: How to run the app that handles subscription and unsubscription
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
```

Step 3:  How to run the app that handles periodic sending of quotes
---------
* go to the folder and run
```
source env.sh
python send_app.py
```
