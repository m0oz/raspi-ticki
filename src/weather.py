from __future__ import annotations
from dataclasses import dataclass
import python_weather
import asyncio


@dataclass
class Weather:
    """Weather data to display on the OLED screen"""

    min_temperature: float
    max_temperature: float

    def print(self) -> str:
        """Print the weather data in a human-readable format"""
        return f"{self.min_temperature:.1f}°C to {self.max_temperature:.0f}°C"

    @staticmethod
    async def _fetch_weather() -> Weather:
        """Internal async method to fetch weather data"""
        async with python_weather.Client(unit=python_weather.METRIC) as client:
            # Hardcoded for Zürich
            weather = await client.get("Hamburg")

            # Get today's forecast
            today = next(iter(weather))

            return Weather(
                min_temperature=today.lowest_temperature, max_temperature=today.highest_temperature
            )

    @classmethod
    def get_weather(cls) -> "Weather":
        """Get weather data for Zürich"""
        try:
            return asyncio.run(cls._fetch_weather())
        except Exception as e:
            # Fallback values if weather fetch fails
            print(f"Failed to fetch weather: {e}")
            return Weather(min_temperature=0.0, max_temperature=0.0)
