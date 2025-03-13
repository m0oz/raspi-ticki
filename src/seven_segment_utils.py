from enum import Enum
from dataclasses import dataclass


class Segment(str, Enum):
    """Seven-segment display segments labeled a-g"""

    A = "a"  # Top
    B = "b"  # Top right
    C = "c"  # Bottom right
    D = "d"  # Bottom
    E = "e"  # Bottom left
    F = "f"  # Top left
    G = "g"  # Middle


@dataclass
class SegmentLocation:
    """Location of a segment in the display data"""

    byte: int  # Which byte in the data (1-4)
    bit: int  # Which bit in the byte (0-7)


class Digit:
    """Represents a digit position (hours tens, hours ones, etc)"""

    def __init__(self, segment_map: dict[Segment, SegmentLocation]):
        self.segments = segment_map

    @staticmethod
    def get_segments_for_digit(digit: int) -> list[Segment]:
        """
        Returns the segments that should be lit for a given digit.

        Args:
            digit: Integer from 0-9

        Returns:
            List of Segments that should be lit
        """
        DIGIT_TO_SEGMENTS = {
            0: [Segment.A, Segment.B, Segment.C, Segment.D, Segment.E, Segment.F],
            1: [Segment.B, Segment.C],
            2: [Segment.A, Segment.B, Segment.D, Segment.E, Segment.G],
            3: [Segment.A, Segment.B, Segment.C, Segment.D, Segment.G],
            4: [Segment.B, Segment.C, Segment.F, Segment.G],
            5: [Segment.A, Segment.C, Segment.D, Segment.F, Segment.G],
            6: [Segment.A, Segment.C, Segment.D, Segment.E, Segment.F, Segment.G],
            7: [Segment.A, Segment.B, Segment.C],
            8: [Segment.A, Segment.B, Segment.C, Segment.D, Segment.E, Segment.F, Segment.G],
            9: [Segment.A, Segment.B, Segment.C, Segment.D, Segment.F, Segment.G],
        }

        if not 0 <= digit <= 9:
            raise ValueError("Digit must be between 0 and 9")

        return DIGIT_TO_SEGMENTS[digit]


# Define segment locations for each digit position
HOUR_ONES = Digit(
    {
        Segment.A: SegmentLocation(3, 6),
        Segment.B: SegmentLocation(3, 5),
        Segment.C: SegmentLocation(3, 4),
        Segment.D: SegmentLocation(3, 3),
        Segment.E: SegmentLocation(4, 7),
        Segment.F: SegmentLocation(3, 1),
        Segment.G: SegmentLocation(3, 0),
    }
)

MINUTE_TENS = Digit(
    {
        Segment.A: SegmentLocation(2, 6),
        Segment.B: SegmentLocation(2, 5),
        Segment.C: SegmentLocation(2, 4),
        Segment.D: SegmentLocation(2, 3),
        Segment.E: SegmentLocation(3, 7),
        Segment.F: SegmentLocation(2, 1),
        Segment.G: SegmentLocation(2, 0),
    }
)

MINUTE_ONES = Digit(
    {
        Segment.A: SegmentLocation(1, 6),
        Segment.B: SegmentLocation(1, 5),
        Segment.C: SegmentLocation(1, 4),
        Segment.D: SegmentLocation(1, 3),
        Segment.E: SegmentLocation(2, 7),
        Segment.F: SegmentLocation(1, 1),
        Segment.G: SegmentLocation(1, 0),
    }
)
