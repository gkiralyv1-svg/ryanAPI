from decimal import Decimal

from ryanapi.cli import build_city_airport_map, filter_available_fares, normalize_city_name
from ryanapi.translations import TRANSLATIONS
from ryanapi.web import VALID_CURRENCIES


def test_normalize_city_name():
    assert normalize_city_name("  Budapest  ") == "budapest"
    assert normalize_city_name("PORTO") == "porto"


def test_build_city_airport_map():
    records = [
        {"city": "Budapest", "iataCode": "BUD"},
        {"city": "Budapest", "iataCode": "FRA"},
        {"city": "Porto", "iataCode": "OPO"},
    ]
    mapping = build_city_airport_map(records)
    assert mapping["budapest"] == ["BUD", "FRA"]
    assert mapping["porto"] == ["OPO"]


def test_filter_available_fares():
    fares = [
        {"unavailable": True, "price": {"value": 50, "currencyCode": "EUR"}},
        {"day": "2026-10-04", "price": {"value": 19.99, "currencyCode": "EUR"}},
        {"day": "2026-10-05", "price": {"value": 40.0, "currencyCode": "EUR"}},
    ]

    assert len(filter_available_fares(fares, max_price=Decimal("30"))) == 1
    assert filter_available_fares(fares)[0]["day"] == "2026-10-04"


def test_currency_validation():
    assert VALID_CURRENCIES == {"EUR", "HUF"}


def test_translation_keys_exist():
    required = {
        "subtitle",
        "origin",
        "destination",
        "month",
        "currency",
        "max_price",
        "search",
        "new_search",
        "results",
        "set_home_city",
        "swap_tooltip",
    }
    assert required.issubset(TRANSLATIONS["hu"])
    assert required.issubset(TRANSLATIONS["en"])


def test_route_mapping_logic():
    routes = [
        {"arrivalAirport": {"code": "OPO"}},
        {"arrivalAirportCode": "BUD"},
        {"arrivalAirport": "MXP"},
    ]
    reachable = {
        route.get("arrivalAirport", {}).get("code")
        or route.get("arrivalAirportCode")
        or route.get("arrivalAirport")
        or ""
        for route in routes
    }
    assert "OPO" in reachable
    assert "BUD" in reachable
    assert "MXP" in reachable
