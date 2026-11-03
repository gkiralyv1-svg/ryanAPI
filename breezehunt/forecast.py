import requests

from breezehunt.scoring import classify_swell


# Open-Meteo API endpoints
MARINE_API_URL = "https://marine-api.open-meteo.com/v1/marine"
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

# Nazaré coordinates
LATITUDE = 39.6115
LONGITUDE = -9.0841

# Local time at the forecast location
TIMEZONE = "Europe/Lisbon"

# Number of forecast days
FORECAST_DAYS = 7


def get_marine_forecast():
    """
    Retrieve hourly swell data for Nazaré.
    """

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": (
            "swell_wave_height,"
            "swell_wave_period,"
            "swell_wave_direction"
        ),
        "forecast_days": FORECAST_DAYS,
        "timezone": TIMEZONE,
    }

    response = requests.get(
        MARINE_API_URL,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    return response.json()


def get_weather_forecast():
    """
    Retrieve hourly wind data for Nazaré.
    """

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": (
            "wind_speed_10m,"
            "wind_direction_10m"
        ),
        "forecast_days": FORECAST_DAYS,
        "timezone": TIMEZONE,
    }

    response = requests.get(
        WEATHER_API_URL,
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    return response.json()


def get_value(values, index):
    """
    Safely retrieve a value from an hourly data list.
    """

    if values is None or index is None:
        return None

    if index >= len(values):
        return None

    return values[index]


def build_forecasts(marine_data, weather_data):
    """
    Combine marine and weather data by timestamp.

    Returns a list of hourly forecast dictionaries.
    """

    marine_hourly = marine_data["hourly"]
    weather_hourly = weather_data["hourly"]

    # Create a lookup table for weather timestamps.
    weather_time_index = {
        timestamp: index
        for index, timestamp in enumerate(weather_hourly["time"])
    }

    forecasts = []

    for marine_index, timestamp in enumerate(marine_hourly["time"]):

        # Find the matching weather timestamp.
        weather_index = weather_time_index.get(timestamp)

        if weather_index is None:
            wind_speed = None
            wind_direction = None
        else:
            wind_speed = get_value(
                weather_hourly.get("wind_speed_10m"),
                weather_index,
            )

            wind_direction = get_value(
                weather_hourly.get("wind_direction_10m"),
                weather_index,
            )

        # Marine data
        swell_height = get_value(
            marine_hourly.get("swell_wave_height"),
            marine_index,
        )

        swell_period = get_value(
            marine_hourly.get("swell_wave_period"),
            marine_index,
        )

        swell_direction = get_value(
            marine_hourly.get("swell_wave_direction"),
            marine_index,
        )

        # Classify the swell conditions.
        level = classify_swell(
            swell_height,
            swell_period,
        )

        forecast = {
            "time": timestamp,
            "swell_height": swell_height,
            "swell_period": swell_period,
            "swell_direction": swell_direction,
            "wind_speed": wind_speed,
            "wind_direction": wind_direction,
            "level": level,
        }

        forecasts.append(forecast)

    return forecasts


def get_forecasts():
    """
    Retrieve and combine marine and weather forecasts.
    """

    marine_data = get_marine_forecast()
    weather_data = get_weather_forecast()

    return build_forecasts(marine_data, weather_data)
def build_daily_summary(forecasts):
    """
    Aggregate hourly forecasts into daily summaries.
    """

    daily_data = {}

    for forecast in forecasts:
        day = forecast["time"][:10]

        daily_data.setdefault(day, []).append(forecast)

    daily_summary = []

    for day, records in daily_data.items():

        heights = [
            r["swell_height"]
            for r in records
            if r["swell_height"] is not None
        ]

        periods = [
            r["swell_period"]
            for r in records
            if r["swell_period"] is not None
        ]

        levels = [
            r["level"]
            for r in records
            if r["level"] is not None
        ]

        max_level = max(levels) if levels else None

        peak_records = [
            r for r in records
            if r["level"] == max_level
        ] if max_level is not None else []

        peak_record = max(
            peak_records,
            key=lambda r: (
                r["swell_height"] if r["swell_height"] is not None else -1,
                r["swell_period"] if r["swell_period"] is not None else -1,
            ),
            default=None,
        )

        daily_summary.append({
            "date": day,
            "min_swell_height": min(heights) if heights else None,
            "max_swell_height": max(heights) if heights else None,
            "avg_swell_period": (
                sum(periods) / len(periods)
                if periods else None
            ),
            "max_level": max_level,
            "peak_time": (
                peak_record["time"] if peak_record else None
            ),
        })

    if daily_summary:
        valid_days = [
            day for day in daily_summary
            if day["max_level"] is not None
        ]

        if valid_days:
            best_day = max(
                valid_days,
                key=lambda day: (
                    day["max_level"],
                    day["max_swell_height"]
                    if day["max_swell_height"] is not None
                    else -1,
                    day["avg_swell_period"]
                    if day["avg_swell_period"] is not None
                    else -1,
                ),
            )

            for day in daily_summary:
                day["is_best_day"] = day is best_day
        else:
            for day in daily_summary:
                day["is_best_day"] = False

    return daily_summary