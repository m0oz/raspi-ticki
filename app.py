from flask import Flask, render_template, request, jsonify
import vlc
import time
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests
import os
import threading

app = Flask(__name__)

# Global variables
current_station = {
    'name': 'SRF2',
    'url': 'https://stream.srg-ssr.ch/drs2/aacp_96.m3u'
}
player = None
is_playing = False
alarm_time = None
scheduler = BackgroundScheduler()
scheduler.start()

def get_stream_url():
    try:
        response = requests.get(current_station['url'])
        return response.text.strip()
    except Exception as e:
        print(f"Error fetching stream URL: {e}")
        return None

def init_player():
    global player
    try:
        if player:
            player.stop()
            player.release()
        
        instance = vlc.Instance('--no-video')  # Audio only
        player = instance.media_player_new()
        stream_url = get_stream_url()
        if stream_url:
            media = instance.media_new(stream_url)
            player.set_media(media)
            return True
    except Exception as e:
        print(f"Error initializing player: {e}")
        return False

def play_radio():
    global player, is_playing
    try:
        if not player or not is_playing:
            if init_player():
                player.play()
                is_playing = True
                return True
        return False
    except Exception as e:
        print(f"Error playing radio: {e}")
        return False

def stop_radio():
    global player, is_playing
    try:
        if player and is_playing:
            player.stop()
            is_playing = False
            return True
        return False
    except Exception as e:
        print(f"Error stopping radio: {e}")
        return False

@app.route('/')
def home():
    return render_template('index.html', 
                         current_station=current_station['name'],
                         alarm_time=alarm_time)

@app.route('/play', methods=['POST'])
def play():
    success = play_radio()
    return jsonify({
        'status': 'success' if success else 'error',
        'message': 'Radio is playing' if success else 'Failed to play radio'
    })

@app.route('/stop', methods=['POST'])
def stop():
    success = stop_radio()
    return jsonify({
        'status': 'success' if success else 'error',
        'message': 'Radio stopped' if success else 'Failed to stop radio'
    })

@app.route('/set_alarm', methods=['POST'])
def set_alarm():
    global alarm_time
    alarm_time = request.form.get('time')
    
    try:
        # Remove existing alarm job if it exists
        scheduler.remove_all_jobs()
        
        # Add new alarm job
        scheduler.add_job(
            play_radio,
            'cron',
            hour=alarm_time.split(':')[0],
            minute=alarm_time.split(':')[1]
        )
        
        return jsonify({
            'status': 'success',
            'message': f'Alarm set for {alarm_time}'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to set alarm: {str(e)}'
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True) 