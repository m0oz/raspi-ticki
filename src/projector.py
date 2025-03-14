import digitalio
import board
import time
import csv
from .seven_segment_utils import MINUTE_ONES, MINUTE_TENS, HOUR_ONES
from pathlib import Path
from typing import List, Tuple


class Projector:
    """Manages SPI communication with 7-segment time projector using bit-banging"""

    def __init__(self):
        """Initialize the display controller with bit-banged SPI."""
        # Setup GPIO pins for bit-banging
        self.sck = digitalio.DigitalInOut(board.SCK)
        self.mosi = digitalio.DigitalInOut(board.MOSI)
        self.enable = digitalio.DigitalInOut(board.CE0)
        self.sck.direction = digitalio.Direction.OUTPUT
        self.mosi.direction = digitalio.Direction.OUTPUT
        self.enable.direction = digitalio.Direction.OUTPUT

        self.replay_from_csv(Path(__file__).parent / "startup.csv")

        # Ensure both pins idle high
        self.sck.value = True
        self.mosi.value = True
        self.enable.value = True

    def bitbang_write(self, data: int, bits: int = 8):
        """Send a byte over SPI using bit-banging."""
        self.enable.value = False
        time.sleep(0.0000005)
        for i in reversed(range(bits)):
            self.mosi.value = (data >> i) & 1
            self.sck.value = False
            time.sleep(0.000000001)
            self.sck.value = True
            time.sleep(0.000001)
        self.mosi.value = True
        time.sleep(0.000001)
        self.enable.value = True
        time.sleep(0.000001)

    def send_time(self, hours: int, minutes: int):
        """Send the time to the display."""
        print(f"Sending time: {hours:02d}:{minutes:02d}")
        data = self.create_clock_event(hours, minutes)
        print(
            f"Sending time: {hours:02d}:{minutes:02d}, binary: {' '.join(format(byte, '08b') for byte in data)}"
        )
        # Send 5 bytes (40 bits) as a single 40-bit sequence
        combined_bits = 0
        for byte in data:
            combined_bits = (combined_bits << 8) | int(byte)
        self.bitbang_write(combined_bits, bits=40)

    def send_binary_event(self, binary_data: str):
        """Send binary data directly to the display."""
        if len(binary_data) != 40:
            raise ValueError("Binary data must be exactly 40 bits long")
        data = bytes(int(binary_data[i : i + 8], 2) for i in range(0, 40, 8))
        print(f"Sending binary event: {binary_data}, bytes: {data.hex()}")
        # Send 5 bytes (40 bits) as a single 40-bit sequence
        combined_bits = 0
        for byte in data:
            combined_bits = (combined_bits << 8) | int(byte)
        self.bitbang_write(combined_bits, bits=40)

    def replay_from_csv(self, csv_path: str):
        """Replay pin changes from a CSV file with columns Time [s],MOSI,CLK,EN."""
        events: List[Tuple[float, bool, bool, bool]] = []

        # Read and parse CSV
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            last_time = None

            for row in reader:
                current_time = float(row["Time [s]"])
                if last_time is None:
                    last_time = current_time

                # Store relative time difference and pin states
                events.append(
                    (
                        current_time - last_time,  # relative time difference
                        bool(int(row["MOSI"])),
                        bool(int(row["CLK"])),
                        bool(int(row["EN"])),
                    )
                )
                last_time = current_time

        # Replay events
        print(f"Replaying {len(events)} events from {csv_path}")
        for delay, mosi, clk, en in events:
            if delay > 0:
                time.sleep(delay)
            self.mosi.value = mosi
            self.sck.value = clk
            self.enable.value = en

    @staticmethod
    def create_clock_event(hours: int, minutes: int) -> bytes:
        """
        Creates a clock event for the given hour and minute

        Args:
            hour: Hour in 24-hour format (0-23)
            minute: Minute (0-59)

        Returns:
            bytes: 5-byte event sequence
        """
        result = bytearray([0xAC, 0x00, 0x00, 0x00, 0x00])

        hour_tens = hours // 10
        hour_ones = hours % 10
        minute_tens = minutes // 10
        minute_ones = minutes % 10

        if hour_tens == 1:
            result[4] |= (1 << 5) | (1 << 6)
        elif hour_tens == 2:
            result[4] |= (1 << 0) | (1 << 6)

        for segment in HOUR_ONES.get_segments_for_digit(hour_ones):
            loc = HOUR_ONES.segments[segment]
            result[loc.byte] |= 1 << loc.bit

        for segment in MINUTE_TENS.get_segments_for_digit(minute_tens):
            loc = MINUTE_TENS.segments[segment]
            result[loc.byte] |= 1 << loc.bit

        for segment in MINUTE_ONES.get_segments_for_digit(minute_ones):
            loc = MINUTE_ONES.segments[segment]
            result[loc.byte] |= 1 << loc.bit

        result[1] |= 1 << 2
        result[2] |= 1 << 2
        result[3] |= 1 << 2

        print(
            f"Created event for {hours:02d}:{minutes:02d}, binary: {' '.join(format(byte, '08b') for byte in result)}"
        )

        return bytes(result)
