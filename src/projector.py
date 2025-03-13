from .seven_segment_utils import MINUTE_ONES, MINUTE_TENS, HOUR_ONES

try:
    import spidev
except ImportError:
    print("Warning: Running in simulation mode - hardware control disabled")

    class MockSpiDev:
        def __init__(self):
            self.max_speed_hz = 0
            self.mode = 0
            self.no_cs = False
            self.cshigh = False
            self.lsbfirst = False
            self.bits_per_word = 0

        def open(self, bus, device):
            print(f"Mock SPI opened on bus {bus}, device {device}")

        def xfer2(self, data):
            print(f"Mock SPI transfer: {data}")

    spidev = type("SpiMock", (), {"SpiDev": MockSpiDev})


class Projector:
    """Manages SPI communication with 7segment time projector"""

    def __init__(self, bus: int = 0, device: int = 0):
        """Initialize the display controller with SPI.

        Args:
            bus: SPI bus number (usually 0)
            device: SPI device number (0 for CE0, 1 for CE1)
        """
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 6410  # 156 microseconds between leading edges
        self.spi.mode = 2  # CPOL=1 (clock idle high), CPHA=1 (data sampled on falling edge)
        self.spi.no_cs = False
        self.spi.cshigh = False
        self.spi.lsbfirst = False
        self.spi.bits_per_word = 8

    def send_time(self, hours: int, minutes: int):
        """Send the time to the display."""
        print(f"Sending time: {hours:02d}:{minutes:02d}")
        data = self.create_clock_event(hours, minutes)
        print(
            f"Sending time: {hours:02d}:{minutes:02d}, binary: {' '.join(format(byte, '08b') for byte in data)}"
        )
        self.send_event(data)

    def send_binary_event(self, binary_data: str):
        """Send binary data directly to the display."""
        if len(binary_data) != 40:
            raise ValueError("Binary data must be exactly 40 bits long")
        data = bytes(int(binary_data[i : i + 8], 2) for i in range(0, 40, 8))
        print(f"Sending binary event: {binary_data}, bytes: {data.hex()}")
        self.send_event(data)

    def send_event(self, data: bytes):
        """Send an event using SPI."""
        if len(data) != 5:
            raise ValueError("Data must be exactly 5 bytes")
        self.spi.xfer2(list(data))  # CE handling is automatic

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
        # Initialize 5 bytes with first 8 bits as 10101100
        result = bytearray([0xAC, 0x00, 0x00, 0x00, 0x00])

        # Convert hour/minute to digits
        hour_tens = hours // 10
        hour_ones = hours % 10
        minute_tens = minutes // 10
        minute_ones = minutes % 10

        if hour_tens == 1:
            result[4] |= (1 << 5) | (1 << 6)
        elif hour_tens == 2:
            result[4] |= (1 << 0) | (1 << 6)

        # Show hour ones digit
        for segment in HOUR_ONES.get_segments_for_digit(hour_ones):
            loc = HOUR_ONES.segments[segment]
            result[loc.byte] |= 1 << loc.bit

        # Show minute tens digit (with leading 0)
        for segment in MINUTE_TENS.get_segments_for_digit(minute_tens):
            loc = MINUTE_TENS.segments[segment]
            result[loc.byte] |= 1 << loc.bit

        # Show minute ones digit
        for segment in MINUTE_ONES.get_segments_for_digit(minute_ones):
            loc = MINUTE_ONES.segments[segment]
            result[loc.byte] |= 1 << loc.bit

        # byte 2 is always 1, we don't know why
        result[1] |= 1 << 2
        result[2] |= 1 << 2
        result[3] |= 1 << 2

        print(
            f"Created event for {hours:02d}:{minutes:02d}, binary: {' '.join(format(byte, '08b') for byte in result)}"
        )

        return bytes(result)
