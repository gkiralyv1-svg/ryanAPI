import os
from datetime import date
from decimal import Decimal
from urllib.parse import urlparse

from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for
from requests.exceptions import HTTPError, RequestException
from .cli import get_airports, get_destinations_for_origin, get_ryanair_fares
from .config import HOME_CITY
from .translations import TRANSLATIONS



app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static",
)
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY",
    "ryanapi-development-secret-key",
)


def get_month_options(selected_month=""):
    today = date.today()
    options = []

    for offset in range(24):
        month_index = today.year * 12 + today.month - 1 + offset
        year, zero_based_month = divmod(month_index, 12)
        month_number = zero_based_month + 1
        options.append({
            "value": f"{year:04d}-{month_number:02d}",
            "year": year,
            "month": month_number,
        })

    option_values = {option["value"] for option in options}
    if selected_month and selected_month not in option_values:
        parts = selected_month.split("-")
        if (
            len(parts) == 2
            and all(part.isascii() and part.isdecimal() for part in parts)
            and 1 <= int(parts[1]) <= 12
        ):
            options.append({
                "value": selected_month,
                "year": int(parts[0]),
                "month": int(parts[1]),
            })

    return options


def current_language():
    language = session.get("language", "hu")
    return language if language in TRANSLATIONS else "hu"


@app.context_processor
def inject_translations():
    language = current_language()
    return {"language": language, "t": TRANSLATIONS[language]}


@app.route("/language/<language>")
def set_language(language):
    if language not in TRANSLATIONS:
        abort(404)

    session["language"] = language
    referrer = request.referrer
    if referrer:
        parsed_referrer = urlparse(referrer)
        if (
            parsed_referrer.netloc == request.host
            and parsed_referrer.path != url_for("search")
        ):
            return redirect(referrer)

    return redirect(url_for("index"))


@app.route("/destinations/<origin>")
def destinations(origin):
    try:
        return jsonify(get_destinations_for_origin(origin))
    except ValueError:
        return jsonify({"error": "Unknown origin city"}), 404
    except RequestException:
        return jsonify({"error": "Route lookup unavailable"}), 502


@app.route("/")
def index():
    airports = get_airports()
    cities = sorted(airports.keys())

    return render_template(
        "index.html",
        cities=cities,
        home_city=HOME_CITY,
        selected_month=date.today().strftime("%Y-%m"),
        month_options=get_month_options(date.today().strftime("%Y-%m")),
        selected_currency="EUR",
        selected_max_price="",
    )


@app.route("/search", methods=["POST"])
def search():
    origin = request.form["origin"]
    destination = request.form["destination"]
    month = request.form.get("month", "").strip()
    currency = request.form.get("currency", "EUR").strip().upper()
    max_price_text = request.form.get("max_price", "").strip()

    airports = get_airports()

    origin_airports = airports[origin]
    destination_airports = airports[destination]

    error = None
    fares = []
    max_price = None
    t = TRANSLATIONS[current_language()]
    if currency not in {"EUR", "HUF"}:
        error = t["error_currency"]
    elif max_price_text and not (max_price_text.isascii() and max_price_text.isdecimal()):
        error = t["error_max_price"]
    elif not month:
        error = t["error_month"]
    else:
        if max_price_text:
            max_price = int(max_price_text)

        try:
            data = get_ryanair_fares(
                origin=origin_airports[0],
                destination=destination_airports[0],
                month=month + "-01",
                currency=currency,
            )
            fares = data.get("outbound", {}).get("fares", [])
            if max_price is not None:
                fares = [
                    fare
                    for fare in fares
                    if fare.get("unavailable")
                    or Decimal(str(fare["price"]["value"])) <= max_price
                ]
        except HTTPError as exc:
            response = exc.response
            status = response.status_code if response is not None else "unknown"
            details = response.text.strip()[:300] if response is not None else str(exc)
            error = t["error_api"].format(status=status, details=details)

    print(fares)

    return render_template(
        "index.html",
        cities=sorted(airports.keys()),
        fares=fares,
        selected_origin=origin,
        selected_destination=destination,
        selected_month=month,
        month_options=get_month_options(month),
        home_city=HOME_CITY,
        selected_currency=currency,
        selected_max_price=max_price_text,
        error=error,
    )

    

if __name__ == "__main__":
    app.run(debug=True)