const originSelect = document.getElementById("origin");
const destinationSelect = document.getElementById("destination");
const swapButton = document.getElementById("swap-cities");
const homeCityCheckbox = document.getElementById("save-home-city");

let destinationRequestId = 0;

function isAvailableCity(city) {
    return Array.from(originSelect.options).some((option) => option.value === city);
}

function readSavedHomeCity() {
    try {
        const savedCity = window.localStorage.getItem("homeCity");
        if (savedCity && isAvailableCity(savedCity)) {
            return savedCity;
        }
        if (savedCity) {
            window.localStorage.removeItem("homeCity");
        }
    } catch {
        // Local storage may be disabled; keep using the server default.
    }
    return null;
}

let savedHomeCity = readSavedHomeCity();
if (!originSelect.dataset.searchOrigin && savedHomeCity) {
    originSelect.value = savedHomeCity;
}

function updateHomeCityCheckbox() {
    homeCityCheckbox.checked = originSelect.value === savedHomeCity;
}

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

originSelect.addEventListener("change", () => {
    updateHomeCityCheckbox();
    updateDestinations();
});

homeCityCheckbox.addEventListener("change", () => {
    try {
        if (homeCityCheckbox.checked) {
            savedHomeCity = originSelect.value;
            window.localStorage.setItem("homeCity", savedHomeCity);
        } else {
            savedHomeCity = null;
            window.localStorage.removeItem("homeCity");
        }
    } catch {
        // Keep the current page usable if local storage is unavailable.
    }
    updateHomeCityCheckbox();
});

swapButton.addEventListener("click", () => {
    const originCity = originSelect.value;
    originSelect.value = destinationSelect.value;
    destinationSelect.value = originCity;
    originSelect.dispatchEvent(new Event("change"));
});

updateHomeCityCheckbox();
updateDestinations();
