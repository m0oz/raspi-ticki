from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from datetime import datetime
from .weather import Weather


class Display:
    """Handles the 128x128 OLED display output

    Pin Connections:
    - SDA -> GPIO2 (Physical pin 3)
    - SCL -> GPIO3 (Physical pin 5)
    - VCC -> 3.3V (Physical pin 1)
    - GND -> Ground (Physical pin 6)
    """

    def __init__(self):
        """Initialize the display."""
        serial = i2c(port=1, address=0x3C)
        self.device = ssd1306(serial)
        self.time_text = "0:00"
        self.alarm_text = "No alarm set"
        self.weather_text = "Weather n/a"
        self._render()

    def _render(self):
        with canvas(self.device) as draw:
            draw.text((0, 0), self.time_text, fill="white", font_size=22, align="justified")
            draw.text((0, 24), self.alarm_text, fill="white", font_size=16, align="justified")
            draw.text((0, 40), self.weather_text, fill="white", font_size=16, align="justified")

    def update_time(
        self,
        current_time: datetime,
        next_alarm: str | None = None,
    ):
        self.time_text = f"{current_time.hour:01d}:{current_time.minute:02d}"
        self.alarm_text = f"Alarm: {next_alarm}" if next_alarm else "No alarm set"
        self._render()

    def update_weather(
        self,
        weather: Weather | None = None,
    ):
        self.weather_text = weather.print() if weather else "Weather n/a"
        self._render()
