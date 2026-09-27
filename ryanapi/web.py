from flask import Flask, render_template, request




from .cli import get_airports, get_ryanair_fares


app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static",
)


@app.route("/")
def index():
    airports = get_airports()
    cities = sorted(airports.keys())

    return render_template(
        "index.html",
        cities=cities,
    )


@app.route("/search", methods=["POST"])
def search():
    origin = request.form["origin"]
    destination = request.form["destination"]
    month = request.form["month"]

    airports = get_airports()

    origin_airports = airports[origin]
    destination_airports = airports[destination]

    data = get_ryanair_fares(
        origin=origin_airports[0],
        destination=destination_airports[0],
        month=month + "-01",
        currency="EUR",
    )
        
    fares = data.get("outbound", {}).get("fares", [])

    print(fares)

    return render_template(
    "index.html",
    cities=sorted(airports.keys()),
    fares=fares,
)

    

if __name__ == "__main__":
    app.run(debug=True)