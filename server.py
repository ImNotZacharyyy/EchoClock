from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import socket

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

current_alert = ""
alert_active = False

def get_local_ip():
    try:
        # Create a socket connection to get the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('current_state', {'alert': current_alert, 'active': alert_active})

@socketio.on('toggle_alert')
def handle_toggle_alert(data):
    global current_alert, alert_active
    alert_text = data['alert']
    
    if alert_active and current_alert == alert_text:
        alert_active = False
        current_alert = ""
    else:
        alert_active = True
        current_alert = alert_text
    
    emit('update_alert', {
        'alert': current_alert,
        'active': alert_active,
        'color': get_alert_color(current_alert)
    }, broadcast=True)

@socketio.on('play_bell')
def handle_bell():
    emit('play_bell', broadcast=True)

def get_alert_color(alert):
    colors = {
        "FIRE ALARM": "red",
        "TORNADO WARNING": "orange",
        "LOCKDOWN": "blue",
        "EARTHQUAKE ALERT": "purple",
        "CHEMICAL SPILL": "yellow",
        "BOMB THREAT": "darkred",
        "INTRUDER ALERT": "brown",
        "POWER OUTAGE": "gray",
        "HAZARDOUS WEATHER": "cyan"
    }
    return colors.get(alert, "white")

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"\nServer running at:")
    print(f"Local:   http://127.0.0.1:5001")
    print(f"Network: http://{local_ip}:5001\n")
    socketio.run(app, debug=True, host='0.0.0.0', port=5001) 