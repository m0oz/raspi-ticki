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
            generated = " ".join(bin(byte)[2:].zfill(8) for byte in generated_event)
            expected = known_events[(hour, minute)]

            assert generated == expected, (
                f"Event mismatch for {hour:02d}:{minute:02d}\n"
                f"Expected: {expected}\n"
                f"Got:      {generated}"
            )


def test_the_time():
    result = Projector.create_clock_event(1, 11)
    assert (
        " ".join(bin(byte)[2:].zfill(8) for byte in result)
        == "10101100 00110100 00110100 00110100 00000000"
    )

    result = Projector.create_clock_event(0, 0)
    assert (
        " ".join(bin(byte)[2:].zfill(8) for byte in result)
        == "10101100 01111110 11111110 11111110 10000000"
    )

    result = Projector.create_clock_event(2, 0)
    assert (
        " ".join(bin(byte)[2:].zfill(8) for byte in result)
        == "10101100 01111110 11111110 11101101 10000000"
    )

    result = Projector.create_clock_event(21, 31)
    assert (
        " ".join(bin(byte)[2:].zfill(8) for byte in result)
        == "10101100 00110100 01111101 00110100 01000001"
    )


def test_create_projector():
    projector = Projector()
    projector.send_time(0, 0)
