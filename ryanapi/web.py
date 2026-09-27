from flask import Flask, render_template

from .cli import get_airports


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


if __name__ == "__main__":
    app.run(debug=True)