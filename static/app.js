const originSelect = document.getElementById("origin");
const destinationSelect = document.getElementById("destination");
const swapButton = document.getElementById("swap-cities");

let destinationRequestId = 0;

async function updateDestinations() {
    const requestId = ++destinationRequestId;
    const selectedDestination = destinationSelect.value;
    const url = originSelect.dataset.destinationsUrl.replace(
        "__origin__",
        encodeURIComponent(originSelect.value),
    );

    try {
        const response = await fetch(url, {
            headers: { Accept: "application/json" },
        });
        if (!response.ok) {
            throw new Error("Destination lookup failed");
        }

        const cities = await response.json();
        if (requestId !== destinationRequestId || !Array.isArray(cities)) {
            return;
        }

        const options = cities.map((city) => {
            const label = city.charAt(0).toUpperCase() + city.slice(1);
            return new Option(label, city);
        });
        destinationSelect.replaceChildren(...options);

        if (cities.includes(selectedDestination)) {
            destinationSelect.value = selectedDestination;
        } else {
            destinationSelect.value = cities[0] ?? "";
        }
    } catch {
        // Keep the existing destination options if route lookup fails.
    }
}

originSelect.addEventListener("change", updateDestinations);

swapButton.addEventListener("click", () => {
    const originCity = originSelect.value;
    originSelect.value = destinationSelect.value;
    destinationSelect.value = originCity;
    originSelect.dispatchEvent(new Event("change"));
});

updateDestinations();
