Step1:
create ‘settings.py’ file with following info:
twilio_account_sid = "<twilio account id>"
twilio_auth_token = "<twilio auth token>"
twilio_number = “<twilio ph number>"

Step 2:
----------
How to run:
1. create virtual env
virtualenv venv
2. activating virtual env
source env.sh
3. install dependencies
pip install -r requirements.txt
4. for testing, set
PRODUCTION = false
for running in production (sending mesgs), set
PRODUCTION = True
5.Now, run the application (handles subscription and unsubscription)
python run.py

Step 3:
---------
For running send app (handles periodic sending of quotes)
1. go to the folder and run
source env.sh
2. python send_app.py
