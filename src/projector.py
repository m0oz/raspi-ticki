from unittest.mock import MagicMock
import time
import csv
from pathlib import Path
from .seven_segment_utils import MINUTE_ONES, MINUTE_TENS, HOUR_ONES

try:
    import board
    import digitalio

    IS_RASPBERRY_PI = True
except (ImportError, NotImplementedError):
    IS_RASPBERRY_PI = False

if not IS_RASPBERRY_PI:

    class MockDigitalInOut:
        """Mock implementation of digitalio.DigitalInOut"""

        def __init__(self, pin):
            self._value = False
            self.direction = None

        @property
        def value(self) -> bool:
            return self._value

        @value.setter
        def value(self, val: bool):
            self._value = val

    class MockDirection:
        """Mock implementation of digitalio.Direction"""

        OUTPUT = "output"
        INPUT = "input"

    class MockBoard:
        """Mock implementation of board pins"""

        SCK = "SCK"
        MOSI = "MOSI"
        CE0 = "CE0"

    digitalio = MagicMock()
    digitalio.DigitalInOut = MockDigitalInOut
    digitalio.Direction = MockDirection
    board = MockBoard()
    print("Running with mock hardware (development mode)")


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

        # pins idle high
        self.sck.value = True
        self.mosi.value = True
        self.enable.value = True

    def bitbang_write(self, data: list[bool], num_bits: int):
        """Send data over SPI using bit-banging."""
        self.enable.value = False
        time.sleep(0.0000005)
        for bit in data[:num_bits]:
            self.mosi.value = bit
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
        if len(data) != 5:
            raise ValueError("Data must be exactly 5 bytes")

        # Convert bytes to list of bits, starting with 1 prefix bit
        bits = [True]  # Prefix bit
        for byte in data:
            # Convert each byte to 8 bits, MSB first
            bits.extend(bool((byte >> i) & 1) for i in range(7, -1, -1))

        # Print bits in groups of 8 for readability
        bits_str = "".join("1" if bit else "0" for bit in bits)
        print(bits_str[0] + " " + " ".join(bits_str[i : i + 8] for i in range(1, len(bits), 8)))

        self.bitbang_write(bits, num_bits=41)  # Send all 41 bits

    def send_binary_event(self, binary_data: str):
        """Send binary data directly to the display."""
        if len(binary_data) != 41:
            raise ValueError("Binary data must be exactly 41 bits long")

        # Convert string of '0' and '1' to list of booleans
        bits = [bool(int(bit)) for bit in binary_data]

        print(f"Sending binary event: {binary_data}")
        self.bitbang_write(bits, num_bits=41)

    def replay_from_csv(self, csv_path: str):
        """Replay pin changes from a CSV file with columns Time [s],MOSI,CLK,EN."""
        events: list[tuple[float, bool, bool, bool]] = []

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
        result = bytearray([0x58, 0x08, 0x08, 0x08, 0x00])

        hour_tens = hours // 10
        hour_ones = hours % 10
        minute_tens = minutes // 10
        minute_ones = minutes % 10

        if hour_tens == 1:
            result[4] |= (1 << 6) | (1 << 7)
        elif hour_tens == 2:
            result[4] |= (1 << 1) | (1 << 7)

        for segment in HOUR_ONES.get_segments_for_digit(hour_ones):
            loc = HOUR_ONES.segments[segment]
            result[loc.byte] |= 1 << loc.bit

        for segment in MINUTE_TENS.get_segments_for_digit(minute_tens):
            loc = MINUTE_TENS.segments[segment]
            result[loc.byte] |= 1 << loc.bit

        for segment in MINUTE_ONES.get_segments_for_digit(minute_ones):
            loc = MINUTE_ONES.segments[segment]
            result[loc.byte] |= 1 << loc.bit

        return bytes(result)
