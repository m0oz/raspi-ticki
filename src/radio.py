from dataclasses import dataclass
from datetime import datetime, time, timedelta
from pathlib import Path
import requests
import vlc
from apscheduler.schedulers.background import BackgroundScheduler
from .projector import Projector


@dataclass
class Station:
    name: str
    url: str


STATIONS: dict[str, Station] = {
    "srf2": Station("SRF 2", "https://stream.srg-ssr.ch/drs2/aacp_96.m3u"),
    "fm4": Station("FM4", "https://orf-live.ors-shoutcast.at/fm4-q2a"),
    "br": Station(
        "BR Klassik",
        "https://dispatcher.rndfnk.com/br/brklassik/live/mp3/mid",
    ),
    "last-christmas": Station(
        "Last Christmas",
        "file://" + (Path(__file__).parents[1] / "mp3/last-christmas.mp3").as_posix(),
    ),
}


@dataclass
class Alarm:
    time: str | None = None
    enabled: bool = False

    def to_dict(self):
        return {"time": self.time, "enabled": self.enabled}


class Radio:
    def __init__(self):
        self.current_station = STATIONS["srf2"]
        self.player = None
        self.is_playing = False
        self.alarms = [Alarm(), Alarm()]
        self.alarm_jobs = [None, None]
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        # Initialize 7segment projector controller
        # Pin assigment: MOSI 19, GND 10, CLOCK 23, CE 24
        self.projector = Projector()

        # Schedule projector updates every second if not already scheduled
        if not self.scheduler.get_job("display_update"):
            self.scheduler.add_job(
                self._update_display,
                "interval",
                seconds=1,
                id="display_update",
            )

        self.init_player()

    def _update_display(self):
        """Update the display with current status."""
        current_time = datetime.now()
        self.projector.send_time(current_time.hour, current_time.minute)

    def cleanup(self):
        """Clean up resources when shutting down."""
        if self.scheduler.running:
            self.scheduler.shutdown()

    def get_stream_url(self):
        try:
            if self.current_station.url.endswith(".m3u"):
                # Handle m3u playlist files
                print(f"Returning m3u playlist URL: {self.current_station.url}")
                return requests.get(self.current_station.url).text.strip()
            # Return direct stream URLs as-is
            print(f"Returning direct stream URL: {self.current_station.url}")
            return self.current_station.url
        except requests.RequestException as e:
            print(f"Error fetching stream URL: {e}")
            return None

    def init_player(self):
        try:
            if self.player:
                self.player.stop()
                self.player.release()
            instance = vlc.Instance("--no-video", "--aout=alsa", "--verbose=1")
            if not instance:
                print("Failed to create VLC instance")
                return False

            self.player = instance.media_player_new()
            if not self.player:
                print("Failed to create media player")
                return False

            stream_url = self.get_stream_url()

            if stream_url:
                self.player.set_media(instance.media_new(stream_url))
                return True

            print("Failed to get stream URL")
            return False
        except Exception as e:
            print(f"Error initializing player: {e}")
            return False

    def play_radio(self):
        if not self.player or not self.is_playing:
            if self.init_player():
                self.player.play()
                self.is_playing = True
                # Add auto-stop job that runs once after 10 minutes
                self.scheduler.add_job(
                    self.stop_radio,
                    "date",
                    run_date=datetime.now() + timedelta(seconds=10),
                    id="auto_stop",
                )
                return True
        return False

    def stop_radio(self):
        if self.player and self.is_playing:
            self.player.stop()
            self.is_playing = False
            return True
        return False

    def set_station(self, station_name: str) -> bool:
        if station_name in STATIONS:
            self.current_station = STATIONS[station_name]
            print(f"Current station is now {self.current_station.name}")
            self.stop_radio()
            print("Stopping radio")
            self.init_player()
            print(f"Station was set to {STATIONS[station_name].name}")
            return True
        return False

    def set_alarm(self, alarm_time: str, enabled: bool, alarm_index: int) -> bool:
        try:
            print(f"Setting alarm {alarm_index} to {alarm_time} with enabled={enabled}")
            if alarm_index not in [0, 1]:
                raise ValueError("Invalid alarm index")

            self.alarms[alarm_index] = Alarm(alarm_time, enabled)
            print(f"s: {self.alarms}")

            # Remove existing job if it exists
            if self.alarm_jobs[alarm_index]:
                print(f"Removing existing job {self.alarm_jobs[alarm_index].id}")
                self.scheduler.remove_job(self.alarm_jobs[alarm_index].id)
                self.alarm_jobs[alarm_index] = None

            if self.alarms[alarm_index].enabled and self.alarms[alarm_index].time:
                print(f"Adding new job for alarm {alarm_index}")
                try:
                    self.alarm_jobs[alarm_index] = self.scheduler.add_job(
                        self.play_radio,
                        "cron",
                        hour=self.alarms[alarm_index].time.split(":")[0],
                        minute=self.alarms[alarm_index].time.split(":")[1],
                        id=f"alarm_trigger_{alarm_index}",
                    )
                    print(f"Job added successfully for alarm {alarm_index}")
                except Exception as e:
                    print(f"Error adding job for alarm {alarm_index}: {e}")
            else:
                print(f"Alarm {alarm_index} is not enabled or time is not set")

            print(f"Alarms: {self.alarms}")
            print(f"Alarm jobs: {self.alarm_jobs}")
            return True
        except Exception as e:
            print(f"Error setting alarm: {e}")
            return False

    def get_next_alarm(self) -> str | None:
        now = datetime.now().time()
        next_alarm = None
        next_alarm_time = None

        for alarm in self.alarms:
            if not alarm.enabled or not alarm.time:
                continue

            alarm_parts = alarm.time.split(":")
            alarm_time = time(int(alarm_parts[0]), int(alarm_parts[1]))

            if next_alarm_time is None or (
                (now > alarm_time and (next_alarm_time is None or alarm_time < next_alarm_time))
                or (now < alarm_time and (next_alarm_time is None or alarm_time < next_alarm_time))
            ):
                next_alarm_time = alarm_time
                next_alarm = alarm.time

        return next_alarm
