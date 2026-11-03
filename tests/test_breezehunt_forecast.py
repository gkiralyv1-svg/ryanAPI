from breezehunt.forecast import build_forecasts


def test_build_forecasts():
    marine_data = {
        "hourly": {
            "time": [
                "2026-11-02T10:00",
                "2026-11-02T11:00",
            ],
            "swell_wave_height": [3.5, 6.2],
            "swell_wave_period": [13, 15],
            "swell_wave_direction": [290, 300],
        }
    }

    weather_data = {
        "hourly": {
            "time": [
                "2026-11-02T10:00",
                "2026-11-02T11:00",
            ],
            "wind_speed_10m": [12, 15],
            "wind_direction_10m": [250, 270],
        }
    }

    forecasts = build_forecasts(marine_data, weather_data)

    assert len(forecasts) == 2

    assert forecasts[0]["swell_height"] == 3.5
    assert forecasts[0]["wind_speed"] == 12
    assert forecasts[0]["level"] == 1

    assert forecasts[1]["swell_height"] == 6.2
    assert forecasts[1]["wind_speed"] == 15
    assert forecasts[1]["level"] == 3


def test_missing_weather_timestamp():
    marine_data = {
        "hourly": {
            "time": [
                "2026-11-02T10:00",
                "2026-11-02T11:00",
            ],
            "swell_wave_height": [3.5, 4.5],
            "swell_wave_period": [13, 14],
            "swell_wave_direction": [290, 300],
        }
    }

    weather_data = {
        "hourly": {
            "time": ["2026-11-02T10:00"],
            "wind_speed_10m": [12],
            "wind_direction_10m": [250],
        }
    }

    forecasts = build_forecasts(marine_data, weather_data)

    assert len(forecasts) == 2

    assert forecasts[0]["wind_speed"] == 12
    assert forecasts[0]["wind_direction"] == 250

    assert forecasts[1]["wind_speed"] is None
    assert forecasts[1]["wind_direction"] is None

    assert forecasts[1]["swell_height"] == 4.5
    assert forecasts[1]["level"] == 2