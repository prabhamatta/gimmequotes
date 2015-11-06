source env.sh
pkill -9 -f run.py
nohup python run.py &
pkill -9 -f send_app.py
nohup python send_app.py &
