from pathlib import Path

from src.projector import Projector


def test_clock_events():
    """
    Test the clock event generation against known values from the CSV
    """
    # Read the CSV file
    with (Path(__file__).parent / "all_time_events.csv").open() as f:
        lines = f.readlines()[1:]  # Skip header

    # Create a dictionary of time -> event mappings from the CSV
    known_events = {}
    for line in lines:
        if "," not in line:
            continue

        time_str, _, event_str_binary = line.strip().split(",")
        hour, minute = map(int, time_str.split(":"))
        known_events[(hour, minute)] = event_str_binary

    # Test all times
    for hour in range(24):
        for minute in range(60):
            if (hour, minute) not in known_events:
                continue

            generated_event = Projector.create_clock_event(hour, minute)
            bits = [True]  # Prefix bit
            for byte in generated_event:
                bits.extend(bool((byte >> i) & 1) for i in range(7, -1, -1))
            bits_str = "".join("1" if bit else "0" for bit in bits)

            expected = known_events[(hour, minute)]

            assert bits_str == expected, (
                f"Event mismatch for {hour:02d}:{minute:02d}\n"
                f"Expected: {expected}\n"
                f"Got:      {bits_str}"
            )


def test_the_time():
    result = Projector.create_clock_event(11, 11)
    assert (
        " ".join(bin(byte)[2:].zfill(8) for byte in result)
        == "01011000 01101000 01101000 01101000 11000000"
    )

    result = Projector.create_clock_event(0, 0)
    assert (
        " ".join(bin(byte)[2:].zfill(8) for byte in result)
        == "01011000 11111101 11111101 11111101 00000000"
    )


def test_create_projector():
    projector = Projector()
    projector.send_time(0, 0)
