from datetime import datetime

from breezehunt.forecast import get_forecasts


def main():
    print()
    print("=" * 75)
    print("HUN TOURISTS GO NAZARE")
    print("=" * 75)

    forecasts = get_forecasts()

    print(f"\nForecast records: {len(forecasts)}")
    print()

    header = (
        f"{'DATE':<12}"
        f"{'TIME':<8}"
        f"{'SWELL':<10}"
        f"{'PERIOD':<10}"
        f"{'DIRECTION':<12}"
        f"{'WIND':<10}"
        f"{'LEVEL':<8}"
    )

    print(header)
    print("-" * 75)

    for forecast in forecasts:
        timestamp = datetime.fromisoformat(forecast["time"])

        swell_height = forecast["swell_height"]
        swell_period = forecast["swell_period"]
        swell_direction = forecast["swell_direction"]
        wind_speed = forecast["wind_speed"]
        level = forecast["level"]

        height_text = (
            f"{swell_height:.2f} m"
            if swell_height is not None
            else "N/A"
        )

        period_text = (
            f"{swell_period:.1f} s"
            if swell_period is not None
            else "N/A"
        )

        direction_text = (
            f"{swell_direction:.0f}°"
            if swell_direction is not None
            else "N/A"
        )

        wind_text = (
            f"{wind_speed:.1f} km/h"
            if wind_speed is not None
            else "N/A"
        )

        print(
            f"{timestamp:%Y-%m-%d}  "
            f"{timestamp:%H:%M}   "
            f"{height_text:<10}"
            f"{period_text:<10}"
            f"{direction_text:<12}"
            f"{wind_text:<10}"
            f"{level if level is not None else 'N/A'}"
        )

    print("-" * 75)


if __name__ == "__main__":
    main()