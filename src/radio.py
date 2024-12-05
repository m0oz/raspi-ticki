import vlc
from apscheduler.schedulers.background import BackgroundScheduler
import requests

class Radio:
    current_station = {
        'name': 'SRF2',
        'url': 'https://stream.srg-ssr.ch/drs2/aacp_96.m3u'
    }
    player = None
    is_playing = False
    alarm_time = None
    alarm_enabled = False
    alarm_job = None
    scheduler: BackgroundScheduler

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.init_player()

    def get_stream_url(self):
        try:
            response = requests.get(self.current_station['url'])
            return response.text.strip()
        except Exception as e:
            print(f"Error fetching stream URL: {e}")
            return None

    def init_player(self):
        try:
            if self.player:
                self.player.stop()
                self.player.release()
            
            # Add more verbose VLC options
            vlc_args = [
                '--no-video',
                '--aout=alsa',
                '--verbose=1'
            ]
            
            instance = vlc.Instance(*vlc_args)
            if not instance:
                print("Failed to create VLC instance")
                return False
                
            self.player = instance.media_player_new()
            if not self.player:
                print("Failed to create media player")
                return False
                
            stream_url = self.get_stream_url()
            if stream_url:
                media = instance.media_new(stream_url)
                self.player.set_media(media)
                return True
            return False
        except Exception as e:
            print(f"Error initializing player: {e}")
            return False

    def play_radio(self):
        try:
            if not self.player or not self.is_playing:
                if self.init_player():
                    self.player.play()
                    self.is_playing = True
                    if self.alarm_job and self.alarm_job.id == 'alarm_trigger':
                        self.scheduler.add_job(
                            self.stop_radio,
                            'date',
                            run_date='+20 minutes',
                            id='auto_stop'
                        )
                    return True
            return False
        except Exception as e:
            print(f"Error playing radio: {e}")
            return False

    def stop_radio(self):
        try:
            if self.player and self.is_playing:
                self.player.stop()
                self.is_playing = False
                return True
            return False
        except Exception as e:
            print(f"Error stopping radio: {e}")
            return False

    def set_alarm(self, alarm_time, enabled=None):
        try:
            self.alarm_time = alarm_time
            if enabled is not None:
                self.alarm_enabled = enabled

            if self.alarm_job:
                self.scheduler.remove_job(self.alarm_job.id)
                self.alarm_job = None

            if self.alarm_enabled and self.alarm_time:
                self.alarm_job = self.scheduler.add_job(
                    self.play_radio,
                    'cron',
                    hour=self.alarm_time.split(':')[0],
                    minute=self.alarm_time.split(':')[1],
                    id='alarm_trigger'
                )
            return True
        except Exception as e:
            print(f"Error setting alarm: {e}")
            return False
