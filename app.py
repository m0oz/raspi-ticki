from flask import Flask, render_template, request, jsonify
from src.radio import Radio

app = Flask(__name__)

# Initialize Radio instance
radio = Radio()

@app.route('/')
def home():
    return render_template('index.html', 
                         current_station=radio.current_station['name'],
                         alarm_time=radio.alarm_time,
                         alarm_enabled=radio.alarm_enabled)

@app.route('/play', methods=['POST'])
def play():
    success = radio.play_radio()
    return jsonify({
        'status': 'success' if success else 'error',
        'message': 'Radio is playing' if success else 'Failed to play radio'
    })

@app.route('/stop', methods=['POST'])
def stop():
    success = radio.stop_radio()
    return jsonify({
        'status': 'success' if success else 'error',
        'message': 'Radio stopped' if success else 'Failed to stop radio'
    })

@app.route('/set_alarm', methods=['POST'])
def set_alarm():
    alarm_time = request.form.get('time')
    enabled = request.form.get('enabled') == 'true'
    
    try:
        success = radio.set_alarm(alarm_time, enabled)
        return jsonify({
            'status': 'success' if success else 'error',
            'message': f'Alarm {"enabled" if enabled else "disabled"} for {alarm_time}'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to set alarm: {str(e)}'
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True) 