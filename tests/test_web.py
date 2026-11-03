from ryanapi import web


def test_search_displays_fares_for_both_directions(monkeypatch):
    airports = {
        "budapest": ["BUD"],
        "barcelona": ["BCN"],
    }
    calls = []

    def fake_get_ryanair_fares(origin, destination, month, currency):
        calls.append((origin, destination, month, currency))
        price = 42 if origin == "BUD" else 57
        return {
            "outbound": {
                "fares": [{
                    "day": "2026-11-10",
                    "departureDate": "2026-11-10T08:00:00",
                    "arrivalDate": "2026-11-10T11:00:00",
                    "price": {"value": price, "currencyCode": currency},
                }],
            },
        }

    monkeypatch.setattr(web, "get_airports", lambda: airports)
    monkeypatch.setattr(web, "get_ryanair_fares", fake_get_ryanair_fares)

    response = web.app.test_client().post(
        "/search",
        data={
            "origin": "budapest",
            "destination": "barcelona",
            "month": "2026-11",
            "currency": "EUR",
        },
    )

    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Budapest → Barcelona" in page
    assert "Barcelona → Budapest" in page
    assert "42.00" in page
    assert "57.00" in page
    assert calls == [
        ("BUD", "BCN", "2026-11-01", "EUR"),
        ("BCN", "BUD", "2026-11-01", "EUR"),
    ]
