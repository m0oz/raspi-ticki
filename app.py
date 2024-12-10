from flask import Flask, jsonify, render_template, request

from src.radio import STATIONS, Radio

app = Flask(__name__)

# Initialize Radio instance
radio = Radio()


@app.route("/")
def home():
    return render_template(
        "index.html",
        STATIONS=STATIONS,
        current_station=radio.current_station.name,
        alarm_times=[alarm.to_dict() for alarm in radio.alarms],
        next_alarm=radio.get_next_alarm(),
        is_playing=radio.is_playing,
    )


@app.route("/play", methods=["POST"])
def play():
    success = radio.play_radio()
    return jsonify(
        {
            "status": "success" if success else "error",
            "message": "Radio is playing" if success else "Failed to play radio",
        },
    )


@app.route("/stop", methods=["POST"])
def stop():
    success = radio.stop_radio()
    return jsonify(
        {
            "status": "success" if success else "error",
            "message": "Radio stopped" if success else "Failed to stop radio",
        },
    )


@app.route("/set_alarm", methods=["POST"])
def set_alarm():
    alarm_time = request.form.get("time")
    assert isinstance(alarm_time, str)

    enabled = request.form.get("enabled") == "true"
    alarm_index = int(request.form.get("alarm_index", 0))

    try:
        success = radio.set_alarm(alarm_time, enabled, alarm_index)
        next_alarm = radio.get_next_alarm()
        return jsonify(
            {
                "status": "success" if success else "error",
                "message": f'Alarm {alarm_index + 1} {"enabled" if enabled else "disabled"} for {alarm_time}',
                "next_alarm": next_alarm if next_alarm else "No alarm set",
            },
        )
    except Exception as e:
        print(f"Failed to set alarm: {e!s}")
        return jsonify({"status": "error", "message": f"Failed to set alarm: {e!s}"})


@app.route("/set_station", methods=["POST"])
def set_station():
    data = request.get_json()
    station_name = data.get("station")
    assert isinstance(station_name, str)

    if radio.set_station(station_name):
        return jsonify(
            {"status": "success", "station_name": STATIONS[station_name].name},
        )

    return jsonify({"status": "error", "message": "Invalid station"})


if __name__ == "__main__":
    # Only used when running directly, not with gunicorn
    app.run(host="0.0.0.0", port=8000, debug=True)
